# NIDS Configuration CI/CD

A self-contained technical infrastructure project that builds, packages, and validates a Python-based NIDS network configuration CLI across Ubuntu and RHEL-family Linux environments.

The project provisions a local Jenkins environment with **Jenkins Configuration as Code (JCasC)** and **Job DSL**, then uses on-demand Docker build agents to create and validate both **DEB** and **RPM** packages.

## What this project demonstrates

- Jenkins Configuration as Code (JCasC)
- Job DSL and Pipeline as Code
- Dynamic Docker-based Jenkins agents
- Ubuntu and AlmaLinux build/test environments
- Parallel DEB and RPM packaging
- Automated package installation and validation
- Linux network-interface configuration and validation
- Python CLI development
- CI artifact publishing

## Architecture

```text
                         GitHub repository
                                |
                                v
                         Jenkins controller
                         (Docker + JCasC)
                                |
                                v
                              Job DSL
                                |
                                v
                     Jenkins package pipeline
                      /                     \
                     v                       v
          Ubuntu Docker agent        AlmaLinux Docker agent
                |                           |
             Build DEB                   Build RPM
                |                           |
                 \                         /
                  +------ Validation ------+
                             |
                             v
                         Artifacts
```

The Jenkins Docker plugin creates build agents on demand. The Ubuntu and AlmaLinux images include Java 21 for compatibility with current Jenkins Remoting.

## Prerequisites

- Docker Desktop (or Docker Engine)
- Docker Compose
- Git
- Internet access for the initial image, package, and Jenkins plugin downloads

No local Java or Python installation is required for the Jenkins workflow; the required runtimes are included in the Docker images.

## Quick start

From the repository root:

```bash
# Build the Linux agent images
docker compose -f dockers/agents-compose.yaml build

# Build and start Jenkins
docker compose -f dockers/jenkins-compose.yaml up -d --build
```

Open Jenkins at:

```text
http://localhost:8080
```

Demo credentials:

```text
Username: Admin
Password: Aa123456
```

The credentials are intentionally local demo credentials for this disposable Jenkins environment and must not be reused for a real Jenkins deployment.

JCasC configures Jenkins automatically and Job DSL creates the `nids-package-build-and-test` pipeline. Open the pipeline in Jenkins and select **Build Now**.

## Clean installation

Jenkins state is persisted in a Docker volume. To remove existing jobs/build history and test the repository as a completely new installation:

```bash
docker compose -f dockers/jenkins-compose.yaml down -v
docker compose -f dockers/agents-compose.yaml build --no-cache
docker compose -f dockers/jenkins-compose.yaml up -d --build
```

`--no-cache` belongs to `docker compose build`; it is intentionally not passed to `docker compose up`.

## Pipeline flow

The pipeline is defined in [`JenkinsFile`](JenkinsFile) and runs Linux packaging and validation across two Docker agent types.

1. Jenkins checks out the repository.
2. Ubuntu agent builds the Debian package (`.deb`).
3. AlmaLinux agent builds the RPM package (`.rpm`).
4. Jenkins archives the generated packages.
5. Packages are installed in their respective Linux environments.
6. The CLI and validator exercise the NIDS configuration behavior.
7. Successful builds publish the package artifacts in Jenkins.

## CLI tool

Main script: [`nids-config.py`](nids-config.py)

Key classes:

- `NIDSConfig`
- `NetworkInterface`

Default configuration path:

```text
/etc/nids/config.yaml
```

Supported actions include:

- `--enable-ipv6` / `--disable-ipv6` - apply kernel IPv6 configuration through `sysctl`.
- `--enable-ipv4` - record IPv4 as enabled and attempt to bring non-loopback interfaces up.
- `--set-prom-ipv6` / `--set-prom-ipv4` - configure promiscuous mode on active interfaces.
- `--configure-all` - configure IPv4, IPv6, and promiscuous mode for active interfaces.
- `--status` - display configuration and interface status.
- `--validate` - run local environment checks.

`--configure-all` intentionally fails when required kernel/network operations cannot be applied rather than silently reporting success.

## Validator

Validation logic is implemented in [`validator.py`](validator.py).

The validator checks the persisted configuration and, when requested, validates kernel IPv6 state and interface/promiscuous-mode behavior. The Jenkins agents therefore require Linux networking utilities and sufficient container capabilities for the tests they execute.

Example:

```bash
python3 validator.py --expect-ipv6 true --expect-ipv4 true --run-configure-all
```

## Jenkins and Docker agent design

The Jenkins controller is configured through [`dockers/jenkins/jenkins-casc.yaml`](dockers/jenkins/jenkins-casc.yaml).

The two dynamic agent images are:

- [`dockers/ubuntu-agent/Dockerfile`](dockers/ubuntu-agent/Dockerfile)
- [`dockers/alma-agent/Dockerfile`](dockers/alma-agent/Dockerfile)

Agents include the build toolchain, Python dependencies, Linux networking utilities, and Java 21 required by current Jenkins Remoting.

Network configuration tests require elevated container capabilities. The Ubuntu agent receives `NET_ADMIN` and `NET_RAW`; the RHEL-family validation agent currently runs privileged because its test flow includes kernel/sysctl changes.

## Useful commands

```bash
# Build agents
docker compose -f dockers/agents-compose.yaml build

# Start Jenkins
docker compose -f dockers/jenkins-compose.yaml up -d --build

# Follow Jenkins logs
docker logs -f jenkins-master

# Stop the environment while preserving Jenkins state
docker compose -f dockers/jenkins-compose.yaml down

# Stop the environment and remove persisted Jenkins state
docker compose -f dockers/jenkins-compose.yaml down -v
```

## Repository map

- Pipeline: [`JenkinsFile`](JenkinsFile)
- Jenkins Configuration as Code: [`dockers/jenkins/jenkins-casc.yaml`](dockers/jenkins/jenkins-casc.yaml)
- Job DSL: [`dockers/jenkins/jobs/nids-pipeline.groovy`](dockers/jenkins/jobs/nids-pipeline.groovy)
- Python CLI: [`nids-config.py`](nids-config.py)
- Validator: [`validator.py`](validator.py)
- Debian packaging: [`dockers/ubuntu-agent/control`](dockers/ubuntu-agent/control)
- RPM packaging: [`dockers/alma-agent/nids-config.spec`](dockers/alma-agent/nids-config.spec)

## Scope

This is a technical demonstration project rather than a production NIDS deployment. It is designed to demonstrate Linux automation, CI/CD, packaging, Docker-based build infrastructure, and automated validation in a reproducible local environment.
