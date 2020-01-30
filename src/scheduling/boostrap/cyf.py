def get_cyf_bootstrap_script(directory, image, arguments):
    script = ''

    script += '#!/bin/bash' + '\n'
    script += 'module add plgrid/tools/singularity/stable' + '\n'
    script += f'singularity run -B {directory}:/local {image} {arguments}' + '\n'

    return script
