pipeline {
    agent any

    environment {
        IMAGE_NAME       = "college-event-ci"
        CONTAINER_NAME   = "college-event-ansible"
        ANSIBLE_CONTAINER = "ansible-docker-lab"
        // Credentials configured in Jenkins → Manage Credentials
        ADMIN_PASSWORD   = credentials('COLLEGE_ADMIN_PASSWORD')
        FLASK_SECRET_KEY = credentials('COLLEGE_FLASK_SECRET')
    }

    stages {

        // ─────────────────────────────────────────────────────────
        // STAGE 1: BUILD
        // ─────────────────────────────────────────────────────────
        stage('Build') {
            steps {
                echo '=============================================='
                echo 'Building College Event Management System Docker Image...'
                echo '=============================================='
                sh 'docker build -t ${IMAGE_NAME} .'
            }
            post {
                success { echo '✅ Docker image built successfully.' }
                failure { echo '❌ Docker image build failed.' }
            }
        }

        // ─────────────────────────────────────────────────────────
        // STAGE 2: TEST
        // ─────────────────────────────────────────────────────────
        stage('Test') {
            steps {
                echo '=============================================='
                echo 'Running Automated Tests for College Event Management System...'
                echo '=============================================='
                sh '''
                    docker run --rm \
                        -e ADMIN_PASSWORD=testpassword123 \
                        -e DATABASE_PATH=/tmp/test_events.db \
                        ${IMAGE_NAME} \
                        python -m pytest test_app.py -v --tb=short
                '''
            }
            post {
                success { echo '✅ All tests passed.' }
                failure {
                    echo '❌ Tests failed. Stopping pipeline — deployment will NOT proceed.'
                    error('Test stage failed. Aborting deployment.')
                }
            }
        }

        // ─────────────────────────────────────────────────────────
        // STAGE 3: DEPLOY WITH ANSIBLE
        // ─────────────────────────────────────────────────────────
        stage('Deploy with Ansible') {
            steps {
                echo '=============================================='
                echo 'Deploying with Ansible...'
                echo '=============================================='

                // Copy latest playbook into the Ansible container
                sh 'docker cp event-deploy.yml ${ANSIBLE_CONTAINER}:/event-deploy.yml'

                // Execute the Ansible playbook inside the Ansible container,
                // passing secure credentials as environment variables.
                sh '''
                    docker exec \
                        -e ADMIN_PASSWORD=${ADMIN_PASSWORD} \
                        -e FLASK_SECRET_KEY=${FLASK_SECRET_KEY} \
                        ${ANSIBLE_CONTAINER} \
                        ansible-playbook \
                            -i /inventory.ini \
                            /event-deploy.yml \
                            -e "admin_password=${ADMIN_PASSWORD}" \
                            -e "flask_secret=${FLASK_SECRET_KEY}"
                '''
            }
            post {
                success { echo '✅ Ansible deployment completed successfully.' }
                failure { echo '❌ Ansible deployment failed.' }
            }
        }

    } // end stages

    post {
        success {
            echo ''
            echo '============================================================'
            echo 'SUCCESS: College Event Management CI/CD Pipeline Completed Successfully!'
            echo 'Application is running at http://localhost:5002'
            echo '============================================================'
        }
        failure {
            echo ''
            echo '============================================================'
            echo 'FAILURE: College Event Management CI/CD Pipeline Failed!'
            echo 'Check the stage logs above to identify the problem.'
            echo '============================================================'
        }
        always {
            echo 'Pipeline execution finished.'
        }
    }
}
