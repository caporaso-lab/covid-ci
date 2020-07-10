#!/bin/bash
#SBATCH --job-name={{ job_name }}
#SBATCH --chdir={{ workdir }}
{% for param, arg in slurm_vars.items() %}
#SBATCH --{{ param|replace('_', '-') }}={{ arg }}
{% endfor %}
#SBATCH --output=stdio.out
#SBATCH --hint=compute_bound

module load anaconda3
conda activate genome-sampler

python job.py