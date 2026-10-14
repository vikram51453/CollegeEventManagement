pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME     = "college-event-web"
        CONTAINER_NAME = "college-event-app"
        HOST_PORT      = "5002"
        CONTAINER_PORT = "5000"
    }

    stages {
        stage('Checkout') {
            steps {
                echo '=== Stage 1: Checkout Source Code ==='
                checkout scm
            }
        }

        stage('Docker Build') {
            steps {
                echo '=== Stage 2: Building Docker Image ==='
                bat '''
                    docker context use desktop-linux 2>NUL || ver >NUL
                    docker build -t %IMAGE_NAME%:latest .
                '''
            }
        }

        stage('Automated Tests') {
            steps {
                echo '=== Stage 3: Running Automated Tests inside Container ==='
                bat '''
                    docker run --rm -e ADMIN_PASSWORD=testpassword123 -e DATABASE_PATH=/tmp/test_events.db %IMAGE_NAME%:latest python -m pytest test_app.py -v --tb=short
                '''
            }
        }

        stage('Docker Deploy') {
            steps {
                echo '=== Stage 4: Deploying Docker Container ==='
                echo "Deploying on isolated Port: ${env.HOST_PORT} (Container: ${env.CONTAINER_NAME})"
                bat '''
                    docker stop %CONTAINER_NAME% 2>NUL || ver >NUL
                    docker rm -f %CONTAINER_NAME% 2>NUL || ver >NUL
                    docker run -d --name %CONTAINER_NAME% -p %HOST_PORT%:%CONTAINER_PORT% -v college_event_data:/app/data --restart unless-stopped %IMAGE_NAME%:latest
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                echo '=== Stage 5: Verifying Website Health Check ==='
                bat '''
                    powershell -NoProfile -ExecutionPolicy Bypass -Command "$ok = $false; for ($i = 0; $i -lt 12; $i++) { try { $r = Invoke-WebRequest -Uri ('http://localhost:' + $env:HOST_PORT + '/') -UseBasicParsing -TimeoutSec 5; if ($r.StatusCode -eq 200) { $ok = $true; break } } catch { Start-Sleep -Seconds 3 } }; if (-not $ok) { Write-Error 'Website health check failed'; exit 1 }; Write-Host 'Website health check passed: HTTP 200 OK'"
                '''
            }
        }
    }

    post {
        success {
            echo ''
            echo '============================================================'
            echo ' SUCCESS: Build, Test, and Docker Deployment Completed!'
            echo ' Your College Event Management Website is LIVE at:'
            echo " http://localhost:${env.HOST_PORT}"
            echo '============================================================'
            echo ''
        }
        failure {
            echo ''
            echo '============================================================'
            echo ' FAILURE: CI/CD Pipeline encountered an error.'
            echo ' Check Console Output for details.'
            echo '============================================================'
            echo ''
        }
    }
}
