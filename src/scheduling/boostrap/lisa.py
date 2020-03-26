def get_lisa_bootstrap_script(directory, image, arguments):
    script = ''

    script += '#!/bin/bash' + '\n'
    script += f'singularity run -B {directory}:/local {image} {arguments}' + '\n'

    return script
