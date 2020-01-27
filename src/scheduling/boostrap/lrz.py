from os.path import basename

def get_lisa_bootstrap_script(directory, image, arguments):
    script = ''

    script += '#!/bin/bash' + '\n'
    script += '#SBATCH --job-name=lofar-download' + '\n'
    script += '#SBATCH --time=0-1:00' + '\n'
    script += '#SBATCH --ntasks=1' + '\n'
    script += '#SBATCH --cpus-per-tasks=8' + '\n'
    script += '#SBATCH --mem=8gb'+ '\n'
    script += '#SBATCH --cluster mpp2'

    script += '\n'

    script += 'module load slurm_setup/defaut' + '\n'
    script += 'module load charliecloud/0.10' + '\n'
    script += 'curl -L https://git.io/JvvIy -o chaplin && chmod +x chaplin' + '\n'
    script += f'./chaplin -n -d {image}' + '\n''

    image = basename(image)

    script += f'ch-run -w {image} -b {directory}:/local -- bash /var/local/entrypoint.sh {arguments}' + '\n'

    script += '\n'
