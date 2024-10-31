Pulumi for Appointment

Herein lies the Pulumi program which manages the infrastructure for Appointment.
Setup

    Install Python 3, pip, and virtualenv
    Install Pulumi
    Configure AWS clients
    Clone this repo
    cd to this directory and set up Pulumi in your shell:

export AWS_DEFAULT_REGION=us-east-1
pulumi login s3://tb-appointment-pulumi
pulumi stack select $ENV

Usage

    pulumi preview: Do a dry run and describe the proposed changes; add --diff to see the details.
    pulumi up: Apply the changes

If you are running against a protected environment, you will have to set TBPULUMI_DISABLE_PROTECTION=True explicitly, or you will not be able to make any changes to the live resources.
Adding new dependencies

Update requirements.txt to include the new dependency, then run the installation within the virtual environment Pulumi has built to operate itself in.

./venv/bin/pip install -U -r requirements.txt

