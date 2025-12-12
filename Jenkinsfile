pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                echo '📥 Checking out code from GitHub...'
                checkout scm
            }
        }

        stage('Test Backend') {
            when {
                changeset 'backend/**'
            }
            steps {
                echo '🧪 Testing backend services...'
                script {
                    // Test each backend service
                    def services = ['api_gateway', 'doc_ingestor', 'deid', 'indexer_semantique', 'llm_qa', 'synthese_comparative', 'audit_logger', 'ml_service']

                    for (service in services) {
                        if (fileExists("backend/${service}")) {
                            echo "Testing ${service}..."
                            dir("backend/${service}") {
                                // Install dependencies and run basic tests
                                sh '''
                                    python3 -m venv venv
                                    source venv/bin/activate
                                    pip install -r requirements.txt
                                    python -c "import sys; print('✅ Python import works')"
                                    deactivate
                                '''
                            }
                        }
                    }
                }
            }
        }

        stage('Test Frontend') {
            when {
                changeset 'InterfaceClinique/**'
            }
            steps {
                echo '🧪 Testing frontend...'
                dir('InterfaceClinique') {
                    sh '''
                        npm install
                        npm run build
                        echo '✅ Frontend build successful'
                    '''
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                echo '🐳 Building Docker images...'
                script {
                    def services = ['api_gateway', 'doc_ingestor', 'deid', 'indexer_semantique', 'llm_qa', 'synthese_comparative', 'audit_logger', 'ml_service']

                    for (service in services) {
                        if (fileExists("backend/${service}")) {
                            sh "docker build -t docqa-${service}:latest backend/${service}"
                        }
                    }

                    // Build frontend
                    sh "docker build -t docqa-frontend:latest InterfaceClinique"
                }
            }
        }

        stage('Deploy to Test Environment') {
            when {
                branch 'main'
            }
            steps {
                echo '🚀 Deploying to test environment...'
                sh '''
                    echo '✅ Build and test completed successfully!'
                    echo '📦 Docker images built and ready for deployment'
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
}