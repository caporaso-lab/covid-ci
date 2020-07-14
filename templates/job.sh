#!/bin/bash
#SBATCH --job-name={{ job_name }}
#SBATCH --chdir={{ workdir }}
#SBATCH --cpus-per-task={{ cpus_per_task}}
#SBATCH --time={{ time }}
#SBATCH --mem={{ mem }}
#SBATCH --output=stdio.out
#SBATCH --hint=compute_bound

module load anaconda3
conda activate genome-sampler

python job.py