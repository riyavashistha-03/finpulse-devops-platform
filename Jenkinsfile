pipeline {
    agent any

    environment {
        APP_NAME = 'finpulse-app'
        APP_VERSION = '1.0.0'
        PORT = '5050'
        FLASK_ENV = 'testing'
        REPORTS_DIR = 'reports'
        DOCKER_IMAGE = "ghcr.io/riyavashistha-03/${APP_NAME}:${APP_VERSION}"
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15'))
        ansiColor('xterm')
    }

    stages {
        stage('Checkout SCM') {
            steps {
                echo "==> [Stage 1/11] Checking out source repository from Git..."
                checkout scm
            }
        }

        stage('Environment Verification') {
            steps {
                echo "==> [Stage 2/11] Verifying build environment runtime tools..."
                bat '''
                    python --version
                    pip --version
                    git --version
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                echo "==> [Stage 3/11] Installing required Python dependencies..."
                bat '''
                    python -m pip install --upgrade pip
                    python -m pip install -r requirements.txt
                '''
            }
        }

        stage('DevSecOps Security Audit') {
            steps {
                echo "==> [Stage 4/11] Executing automated SAST & credential leakage scan..."
                bat '''
                    python scripts/security_scan.py
                '''
            }
        }

        stage('Automated Pytest Suite') {
            steps {
                echo "==> [Stage 5/11] Running automated test suite with JUnit XML reporting..."
                bat '''
                    if not exist reports mkdir reports
                    python -m pytest -v --junitxml=reports/pytest-results.xml --cov=app --cov-report=html:reports/coverage-html --cov-report=term tests/
                '''
            }
        }

        stage('Publish Test & Coverage Reports') {
            steps {
                echo "==> [Stage 6/11] Publishing test telemetry in Jenkins..."
                junit allowEmptyResults: true, testResults: 'reports/pytest-results.xml'
            }
        }

        stage('Docker Image Build') {
            steps {
                echo "==> [Stage 7/11] Building multi-stage production Docker image..."
                bat '''
                    docker build -t %DOCKER_IMAGE% -t %APP_NAME%:latest .
                '''
            }
        }

        stage('Container Image Scan') {
            steps {
                echo "==> [Stage 8/11] Auditing Docker container image layers..."
                bat '''
                    docker history %APP_NAME%:latest
                '''
            }
        }

        stage('Container Deployment') {
            steps {
                echo "==> [Stage 9/11] Deploying container for staging validation..."
                bat '''
                    docker stop finpulse-ci-test 2>nul || exit 0
                    docker rm finpulse-ci-test 2>nul || exit 0
                    docker run -d --name finpulse-ci-test -p %PORT%:5050 -e FLASK_ENV=production -e SECRET_KEY=ci-secret-key-9988 %APP_NAME%:latest
                '''
            }
        }

        stage('Health Probe Verification') {
            steps {
                echo "==> [Stage 10/11] Probing /health and /live container endpoints..."
                bat '''
                    timeout /t 8 /nobreak
                    curl -f http://localhost:%PORT%/health || exit /b 1
                    curl -f http://localhost:%PORT%/live || exit /b 1
                    curl -f http://localhost:%PORT%/metrics || exit /b 1
                '''
            }
        }

        stage('Archive Build Artifacts') {
            steps {
                echo "==> [Stage 11/11] Archiving test reports and Capstone documentation..."
                archiveArtifacts artifacts: 'reports/**, docs/*.pdf', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            echo "==> Cleaning up transient test container..."
            bat '''
                docker stop finpulse-ci-test 2>nul || exit 0
                docker rm finpulse-ci-test 2>nul || exit 0
            '''
        }
        success {
            echo "==> [PIPELINE SUCCESS] FinPulse CI/CD execution completed successfully!"
        }
        failure {
            echo "==> [PIPELINE FAILURE] Build failed. Inspect step logs above for root cause."
        }
    }
}
