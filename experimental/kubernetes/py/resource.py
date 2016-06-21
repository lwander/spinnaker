import subprocess as sp
import os
import time
import sys

class ResourceExistsError(Exception):
    def __init(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class Resource(object):
    def __init__(self, name, depends_on=[], recreate_list=[]):
        """A node in a resource graph.

        name: [String] Name/ID of this resource.
        depends_on: [List<Resource>] Resources that this depends on.
        recreate_list: [List<String>] A list of strings that need to be
            recreated during this execution.
        """

        self.name = name
        self.depends_on = depends_on
        self.created = False
        self.drawn = False
        self.recreate = False
        self.force_recreate = self.name in recreate_list

    def create(self, recreate=False):
        """Create this node in the graph.

        recreate: [Boolean] Will delete resource before creating when True
        """
        if recreate:
            print 'Deleting {}'.format(self.name)
            self._delete()

        print 'Creating {}'.format(self.name)
        self.created = True
        self._create()


    def draw(self):
        """Generate DOT formated entries for this node in the resource graph"""
        if self.drawn:
            return self.recreate

        # This will indicate whether or not this resource needs to be recreated
        # during the build().
        self.recreate = self.force_recreate

        for r in self.depends_on:
            print '{} -> {}'.format(r.name, self.name)

        for r in self.depends_on:
            self.recreate = r.draw() or self.recreate

        if self.recreate:
            print '{} [color="red"]'.format(self.name)

        self.drawn = True

        return self.recreate

    def build(self):
        """Build this resource. Return True when (re)created, False otherwise.
        """
        if self.created:
            return

        recreate = False

        # If something this depends on is recreated, this needs to be as well.
        for r in self.depends_on:
            recreate = r.build() or recreate

        recreate = recreate or self.force_recreate

        try:
            self.create(recreate=recreate)

        except ResourceExistsError:
            print ('Notice: resource {} already exists and won\'t be modified'
                .format(self.name))
        except Exception as e:
            print 'Fatal: {}'.format(e)
            exit(1)


    def _delete(self):
        pass

    def _create(self):
        pass

class KubernetesResource(Resource):
    """A Resource that can be created with `kubectl create -f <filename>`"""
    def __init__(self, name, config=None, namespace='default', depends_on=[],
            recreate_list=[]):
        """Initialize the resource node.

        name: [String] Unique name for the resource.
        config: [String] Path to kubernetes config file holding resource.
        namespace: [String] Namespace this will be installed in.
        depends_on: [List<Resource>] Resources that this depends on.
        recreate_list: [List<String>] A list of strings that need to be
            recreated during this execution.
        """
        if config is None:
            raise ValueError("`config` is required to create resource")

        Resource.__init__(self, name, depends_on=depends_on,
                recreate_list=recreate_list)

        self.config = config
        self.namespace = namespace

    def _exists(self):
        cmd = ['kubectl', 'get', '-f', self.config, 
                '--namespace', self.namespace]

        try:
            sp.check_output(cmd, stderr=sp.STDOUT)
        except sp.CalledProcessError as err:
            return False
        except Exeception as e:
            raise e

        return True

    def _delete(self):
        cmd = ['kubectl', 'delete', '-f', self.config, 
                '--namespace', self.namespace]
        try:
            sp.check_output(cmd, stderr=sp.STDOUT)
        except sp.CalledProcessError as err:
            if err.output is not None and 'not found' in err.output:
                print 'Warning: Resource ' + self.name + ' not found'
            else:
                raise err

        sys.stdout.write('Waiting until {} is deleted'.format(self.name))
        try:
            while self._exists():
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(2)
        except Exception as e:
            sys.stdout.write('\n')
            sys.stdout.flush()
            raise e

        sys.stdout.write('\n')
        sys.stdout.flush()

    def _create(self):
        cmd = ['kubectl', 'create', '-f', self.config, 
                '--namespace', self.namespace]
        try:
            sp.check_output(cmd, stderr=sp.STDOUT)
            time.sleep(2)
        except sp.CalledProcessError as err:
            if err.output is not None and 'already exists' in err.output:
                raise ResourceExistsError()
            else:
                raise err

        sys.stdout.write('Waiting until {} is created'.format(self.name))
        try:
            while not self._exists():
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(2)
        except Exception as e:
            sys.stdout.write('\n')
            sys.stdout.flush()
            raise e

        sys.stdout.write('\n')
        sys.stdout.flush()

class KubernetesSecret(Resource):
    def __init__(self, name, secret_name=None, contents=[], namespace='default',
            depends_on=[], recreate_list=[]):
        """Initialize a Kubernetes Secret

        name: [String] Unique name for the resource.
        secret_name: [String] The name the secret has in Kubernetes.
        namespace: [String] Namespace this will be installed in.
        contents: [List<File>] List of files to be included.
        recreate_list: [List<String>] A list of strings that need to be
            recreated during this execution.
        """
        Resource.__init__(self, name, depends_on=depends_on,
                recreate_list=recreate_list)

        self.secret_name = secret_name
        self.contents = contents
        self.namespace = namespace

    def _delete(self):
        cmd = ['kubectl', 'delete', 'secret', self.secret_name,
                        '--namespace', self.namespace]
        try:
            sp.check_output(cmd, stderr=sp.STDOUT)
        except sp.CalledProcessError as err:
            if err.output is not None and 'not found' in err.output:
                print 'Warning: Resource ' + self.name + ' not found'
            else:
                raise err

    def _create(self):
        cmd = ['kubectl', 'create', 'secret', 'generic', self.secret_name]

        for f in self.contents:
            cmd += ['--from-file', f]

        cmd += ['--namespace', self.namespace]

        try:
            sp.check_output(cmd, stderr=sp.STDOUT)
        except sp.CalledProcessError as err:
            if err.output is not None and 'already exists' in err.output:
                raise ResourceExistsError()
            else:
                raise err

class SpinnakerConfig(Resource):
    def __init__(self, name, namespace=None, depends_on=[], recreate_list=[]):
        self.contents_dir = './config'

        Resource.__init__(self, name, recreate_list=recreate_list, 
                depends_on=depends_on)

    def copy_dir(self, source, target):
        source_files = [os.path.join(source, f)
                for f in os.listdir(source)
                if os.path.isfile(os.path.join(source, f))]

        for f in source_files:
            sp.check_call(['cp', f, target])

    def _create(self):
        try:
            sp.check_output(['mkdir', self.contents_dir], stderr=sp.STDOUT)
        except sp.CalledProcessError as err:
            if err.output is not None and 'File exists' in err.output:
                pass
            else:
                raise err

        self.copy_dir('../../config', self.contents_dir)
        self.copy_dir('./config-source', self.contents_dir)
        self.contents = [os.path.join(self.contents_dir, f)
                for f in os.listdir(self.contents_dir)
                if os.path.isfile(os.path.join(self.contents_dir, f))]

    def _delete(self):
        sp.check_call(['rm', '-r', self.contents_dir])
