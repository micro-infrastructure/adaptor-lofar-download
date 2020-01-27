def get_lisa_bootstrap_script(directory, image, arguments):
    script = ''

    script += '#!/bin/bash' + '\n'
    script += '#SBATCH --job-name=lofar-download' + '\n'
    script += '#SBATCH --time=0-1:00' + '\n'
    script += '#SBATCH --ntasks=1' + '\n'
    script += '#SBATCH --cpus-per-tasks=8' + '\n'
    script += '#SBATCH --mem=8gb'+ '\n'

    script += '\n'

    script += f'singularity run -B {directory}:/local {IMAGE} {arguments}' + '\n'

    script += '\n'
