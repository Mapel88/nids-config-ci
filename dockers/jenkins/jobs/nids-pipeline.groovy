// dockers/jenkins/jobs/nids-pipeline.groovy
pipelineJob('nids-package-build-and-test') {
    description('Builds and tests NIDS configuration packages for RHEL-family Linux and Ubuntu.')
    definition {
        cpsScm {
            scm {
                git {
                    remote {
                        url('https://github.com/Mapel88/nids-config-ci.git')
                    }
                    branch('*/master')
                }
            }
            scriptPath('JenkinsFile')
            lightweight()
        }
    }
}
