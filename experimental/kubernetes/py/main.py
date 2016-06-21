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

def main():
    parser = arg.ArgumentParser(
            description='Install and update Spinnaker on Kubernetetes.')

    parser.add_argument('--kubeconfig',
            help=('Fully qualified path to your kubeconfig file.'
                + 'Default is the default kubeconfig path.'),
            default=os.path.join(os.path.expanduser('~'), '.kube', 'config'))

    parser.add_argument('--gcp-service-account',
            help='Fully qualified path to your gcp service account file.')

    parser.add_argument('--manage-context',
            help=('Context Spinnaker installation will manage. '
                + 'Default is contents of `current-context`.'),
            default=None)

    parser.add_argument('--force-recreate',
            help='Recreate all affected resources without warning.',
            default=False,
            action='store_true')

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

    gcp_config = resource.KubernetesSecret('gcp_config',
            secret_name='gcp-config', contents=[args['gcp_service_account']],
            namespace=install_namespace, recreate_list=recreate_list,
            depends_on=[namespace])

    default_config = ['config/spinnaker.yml', 'config/spinnaker-local.yml']

    clouddriver_config = resource.KubernetesSecret('clouddriver_config',
            contents=default_config + 
                ['config/clouddriver.yml', 'config/clouddriver-local.yml'],
            namespace=install_namespace, recreate_list=recreate_list,
            depends_on=[spinnaker_config])

    clouddriver_svc = resource.KubernetesResource('clouddriver_svc',
            config='rcs/spin-clouddriver.yaml', namespace=install_namespace,
            recreate_list=recreate_list,
            depends_on=[clouddriver_config, kubeconfig, gcp_config])

    clouddriver_rc = resource.KubernetesResource('clouddriver_rc',
            config='svcs/spin-clouddriver.yaml', namespace=install_namespace,
            recreate_list=recreate_list,
            depends_on=[clouddriver_svc])

    orca_config = resource.KubernetesSecret('orca_config',
            contents=default_config + 
                ['config/orca.yml', 'config/orca-local.yml'],
            namespace=install_namespace, recreate_list=recreate_list,
            depends_on=[spinnaker_config])

    orca_svc = resource.KubernetesResource('orca_svc',
            config='rcs/spin-orca.yaml', namespace=install_namespace,
            recreate_list=recreate_list,
            depends_on=[orca_config])

    orca_rc = resource.KubernetesResource('orca_rc',
            config='svcs/spin-orca.yaml', namespace=install_namespace,
            recreate_list=recreate_list,
            depends_on=[orca_svc])

    deck_config = resource.KubernetesSecret('deck_config',
            contents=['config/settings.js'],
            namespace=install_namespace, recreate_list=recreate_list,
            depends_on=[spinnaker_config])

    deck_svc = resource.KubernetesResource('deck_svc',
            config='rcs/spin-deck.yaml', namespace=install_namespace,
            recreate_list=recreate_list,
            depends_on=[deck_config])

    deck_rc = resource.KubernetesResource('deck_rc',
            config='svcs/spin-deck.yaml', namespace=install_namespace,
            recreate_list=recreate_list,
            depends_on=[deck_svc])

    gate_config = resource.KubernetesSecret('gate_config',
            contents=default_config + 
                ['config/gate.yml', 'config/gate-local.yml'],
            namespace=install_namespace, recreate_list=recreate_list,
            depends_on=[spinnaker_config])

    gate_svc = resource.KubernetesResource('gate_svc',
            config='rcs/spin-gate.yaml', namespace=install_namespace,
            recreate_list=recreate_list,
            depends_on=[gate_config])

    gate_rc = resource.KubernetesResource('gate_rc',
            config='svcs/spin-gate.yaml', namespace=install_namespace,
            recreate_list=recreate_list,
            depends_on=[gate_svc])

    igor_config = resource.KubernetesSecret('igor_config',
            contents=default_config + 
                ['config/igor.yml', 'config/igor-local.yml'],
            namespace=install_namespace, recreate_list=recreate_list,
            depends_on=[spinnaker_config])

    igor_svc = resource.KubernetesResource('igor_svc',
            config='rcs/spin-igor.yaml', namespace=install_namespace,
            recreate_list=recreate_list,
            depends_on=[igor_config])

    igor_rc = resource.KubernetesResource('igor_rc',
            config='svcs/spin-igor.yaml', namespace=install_namespace,
            recreate_list=recreate_list,
            depends_on=[igor_svc])

    echo_config = resource.KubernetesSecret('echo_config',
            contents=default_config + 
                ['config/echo.yml', 'config/echo-local.yml'],
            namespace=install_namespace, recreate_list=recreate_list,
            depends_on=[spinnaker_config])

    echo_svc = resource.KubernetesResource('echo_svc',
            config='rcs/spin-echo.yaml', namespace=install_namespace,
            recreate_list=recreate_list,
            depends_on=[echo_config])

    echo_rc = resource.KubernetesResource('echo_rc',
            config='svcs/spin-echo.yaml', namespace=install_namespace,
            recreate_list=recreate_list,
            depends_on=[echo_svc])

    front50_config = resource.KubernetesSecret('front50_config',
            contents=default_config + 
                ['config/front50.yml', 'config/front50-local.yml'],
            namespace=install_namespace, recreate_list=recreate_list,
            depends_on=[spinnaker_config])

    front50_svc = resource.KubernetesResource('front50_svc',
            config='rcs/spin-front50.yaml', namespace=install_namespace,
            recreate_list=recreate_list,
            depends_on=[front50_config])

    front50_rc = resource.KubernetesResource('front50_rc',
            config='svcs/spin-front50.yaml', namespace=install_namespace,
            recreate_list=recreate_list,
            depends_on=[front50_svc])

    aggregate = resource.Resource('aggregate',
            depends_on=[orca_rc, clouddriver_rc, gate_rc, echo_rc, deck_rc,
                front50_rc, igor_rc])

    if (args['draw_graph']):
        print 'digraph {'
        aggregate.draw()
        print '}'

    else:
        aggregate.build()

if __name__ == '__main__':
    main()
