FROM python:3.9.13

# Update and install system packages
RUN apt-get update -y && \
  apt-get install --no-install-recommends -y -q \
  git libpq-dev && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set environment variables
ENV DBT_DIR /dbt

# Set working directory
WORKDIR $DBT_DIR

# Copy requirements
COPY requirements.txt .

# Install DBT
RUN pip install -U pip
RUN pip install -r requirements.txt

# Add dbt_project_1 to the docker image
# COPY dbt_project_1 ./dbt_project_1
# RUN ["dbt", "deps", "--project-dir", "./dbt_project_1"]

# # Add dbt_project_2 to the docker image
# # Repeat these line for every project in the repository
# COPY dbt_project_2 ./dbt_project_2
# RUN ["dbt", "deps", "--project-dir", "./dbt_project_2"]


COPY dbt_project_4 ./dbt_project_4
RUN ["dbt", "deps", "--project-dir", "./dbt_project_4"]

