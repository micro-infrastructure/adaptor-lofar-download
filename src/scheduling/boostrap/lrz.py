from os.path import basename

def get_lrz_bootstrap_script(directory, image, arguments):
    image = 'microinfrastructure/adaptor-lofar-download-hpc'

    script = ''

    script += '#!/bin/bash' + '\n'
    script += 'module load slurm_setup/defaut' + '\n'
    script += 'module load charliecloud' + '\n'
    script += 'curl -L https://git.io/JvvIy -o chaplin && chmod +x chaplin' + '\n'
    script += f'./chaplin -d {image}' + '\n'

    image = basename(image)

    script += f'ch-run -c "/home/$USER" -w {image} -b {directory}:/local -- bash /var/local/entrypoint.sh {arguments}' + '\n'

    return script
