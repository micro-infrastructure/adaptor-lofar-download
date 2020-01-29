from .cyf import get_cyf_bootstrap_script
from .das5 import get_das5_bootstrap_script
from .lisa import get_lisa_bootstrap_script
from .lrz import get_lrz_bootstrap_script

__DAS5 = [
    'fs0.das5.cs.vu.nl',
    'fs1.das5.liacs.nl',
    'fs2.das5.science.uva.nl',
    'fs3.das5.tudelft.nl',
    'fs4.das5.science.uva.nl',
    'fs5.das5.astron.nl'
]

def get_bootstrap_generator(login_node):
    if login_node == 'pro.cyfronet.pl':
        return get_cyf_bootstrap_script

    if __DAS5.contains(login_node):
        return get_das5_bootstrap_script

    if login_node == 'lisa.surfsara.nl':
        return get_lisa_bootstrap_script

    if login_node.endswith('.lrz.de'):
        return get_lrz_bootstrap_script
