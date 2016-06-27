import argparse as arg
import yaml
import os.path
import resource

namespace_config = 'namespaces/namespace.yaml'

def get_config(path):
    contents = None
    with open(path, 'r') as stream:
        contents = yaml.load(stream)

    return contents

def spinnaker_resource(name, namespace, recreate_list, spinnaker_config,
        required_configs=[]):

    config = []
    if name == 'deck':
        config = ['config/settings.js']
    else:
        config = ['config/spinnaker.yml', 
                'config/spinnaker-local.yml',
                'config/{}.yml'.format(name), 
                'config/{}-local.yml'.format(name)]

    config = resource.KubernetesSecret('{}_config'.format(name),
            contents=config,
            namespace=namespace, recreate_list=recreate_list,
            depends_on=[spinnaker_config])

    svc = resource.KubernetesResource('{}_svc'.format(name),
            config='rcs/spin-{}.yaml'.format(name), 
            namespace=namespace,
            recreate_list=recreate_list,
            depends_on=[config] + required_configs)

    rc = resource.KubernetesResource('{}_rc'.format(name),
            config='svcs/spin-{}.yaml'.format(name), 
            namespace=namespace,
            recreate_list=recreate_list,
            depends_on=[svc])

    return rc



def main():
    parser = arg.ArgumentParser(
            description='Install and update Spinnaker on Kubernetetes.')

    parser.add_argument('--kubeconfig',
            help=('Fully qualified path to your kubeconfig file.'
                + 'Default is the default kubeconfig path.'),
            default=os.path.join(os.path.expanduser('~'), '.kube', 'config'))

    parser.add_argument('--gcp-service-account',
            help='Fully qualified path to your gcp service account file.')

    parser.add_argument('--draw-graph',
            help='Print a DOT formated graph to show resource dependencies.',
            default=False,
            action='store_true')

    parser.add_argument('--recreate',
            help='List of resources to be recreated.',
            default=[],
            nargs='*',
            type=str)

    args = vars(parser.parse_args())

    install_namespace = get_config(namespace_config)['metadata']['name']
    recreate_list = args['recreate']

    namespace = resource.KubernetesResource('spinnaker_namespace',
            config='namespaces/namespace.yaml', namespace=install_namespace,
            recreate_list=recreate_list, depends_on=[])

    spinnaker_config = resource.SpinnakerConfig('spin_config',
            namespace=install_namespace, recreate_list=recreate_list,
            depends_on=[namespace])

    kubeconfig = resource.KubernetesSecret('kubeconfig',
            secret_name='kube-config', contents=[args['kubeconfig']],
            namespace=install_namespace, recreate_list=recreate_list,
            depends_on=[namespace])

    clouddriver_configs = kubeconfig

    if (
    gcp_config = resource.KubernetesSecret('gcp_config',
            secret_name='gcp-config', contents=[args['gcp_service_account']],
            namespace=install_namespace, recreate_list=recreate_list,
            depends_on=[namespace])

    clouddriver = spinnaker_resource('clouddriver', install_namespace,
            recreate_list, spinnaker_config, 
            required_configs=[kubeconfig, gcp_config])

    orca = spinnaker_resource('orca', install_namespace,
            recreate_list, spinnaker_config)

    deck = spinnaker_resource('deck', install_namespace,
            recreate_list, spinnaker_config)

    gate = spinnaker_resource('gate', install_namespace,
            recreate_list, spinnaker_config)

    igor = spinnaker_resource('igor', install_namespace,
            recreate_list, spinnaker_config)

    echo = spinnaker_resource('echo', install_namespace,
            recreate_list, spinnaker_config)

    front50 = spinnaker_resource('front50', install_namespace,
            recreate_list, spinnaker_config)

    rosco = spinnaker_resource('rosco', install_namespace,
            recreate_list, spinnaker_config)

    aggregate = resource.Resource('aggregate',
            depends_on=[orca, clouddriver, gate, echo, deck, 
                front50, igor, rosco])

    if (args['draw_graph']):
        print 'digraph {'
        aggregate.draw()
        print '}'

    else:
        aggregate.build()

if __name__ == '__main__':
    main()
