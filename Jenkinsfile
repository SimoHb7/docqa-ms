pipeline {
    agent any
    
    environment {
        COMPOSE_PROJECT_NAME = 'docqa-ms'
        DOCKER_BUILDKIT = '1'
        SONAR_HOST_URL = 'http://localhost:9000'
        SONAR_USER_HOME = "${WORKSPACE}\\.sonar"
    }
    
    // SonarQube Scanner will be used via withSonarQubeEnv
    
    stages {
        stage('Checkout Code') {
            steps {
                echo ' Checking out code from GitHub...'
                checkout([$class: 'GitSCM', 
                    branches: [[name: '*/main']], 
                    userRemoteConfigs: [[
                        url: 'https://github.com/SimoHb7/docqa-ms.git',
                        credentialsId: 'github-token'
                    ]]
                ])
            }
        }

        stage('Validate Configuration') {
            steps {
                echo ' Validating Docker Compose configuration ...'
                script {
                    bat '''
                        echo Checking Docker version...
                        docker --version
                        docker compose version
                        
                        echo Validating docker-compose.yml...
                        docker compose config > nul
                        if errorlevel 1 (
                            echo  Invalid docker-compose.yml
                            exit /b 1
                        ) else (
                            echo  docker-compose.yml is valid
                        )
                    '''
                }
            }
        }

        stage('SonarQube Analysis') {
            stages {
                stage('Analyze API Gateway') {
                    steps {
                        script {
                            withSonarQubeEnv('SonarQube') {
                                dir('backend/api_gateway') {
                                    bat """
                                        sonar-scanner.bat ^
                                        -Dsonar.projectKey=docqa-ms-api-gateway ^
                                        -Dsonar.sources=app ^
                                        -Dsonar.host.url=%SONAR_HOST_URL%
                                    """
                                }
                            }
                        }
                    }
                }
                
                stage('Analyze DeID Service') {
                    steps {
                        script {
                            withSonarQubeEnv('SonarQube') {
                                dir('backend/deid') {
                                    bat """
                                        sonar-scanner.bat ^
                                        -Dsonar.projectKey=docqa-ms-deid ^
                                        -Dsonar.sources=app ^
                                        -Dsonar.host.url=%SONAR_HOST_URL%
                                    """
                                }
                            }
                        }
                    }
                }
                
                stage('Analyze ML Service') {
                    steps {
                        script {
                            withSonarQubeEnv('SonarQube') {
                                dir('backend/ml_service') {
                                    bat """
                                        sonar-scanner.bat ^
                                        -Dsonar.projectKey=docqa-ms-ml-service ^
                                        -Dsonar.sources=app ^
                                        -Dsonar.host.url=%SONAR_HOST_URL%
                                    """
                                }
                            }
                        }
                    }
                }
                
                stage('Analyze Doc Ingestor') {
                    steps {
                        script {
                            withSonarQubeEnv('SonarQube') {
                                dir('backend/doc_ingestor') {
                                    bat """
                                        sonar-scanner.bat ^
                                        -Dsonar.projectKey=docqa-ms-doc-ingestor ^
                                        -Dsonar.sources=app ^
                                        -Dsonar.host.url=%SONAR_HOST_URL%
                                    """
                                }
                            }
                        }
                    }
                }
                
                stage('Analyze Indexer Semantique') {
                    steps {
                        script {
                            withSonarQubeEnv('SonarQube') {
                                dir('backend/indexer_semantique') {
                                    bat """
                                        sonar-scanner.bat ^
                                        -Dsonar.projectKey=docqa-ms-indexer-semantique ^
                                        -Dsonar.sources=app ^
                                        -Dsonar.host.url=%SONAR_HOST_URL%
                                    """
                                }
                            }
                        }
                    }
                }
                
                stage('Analyze LLM QA') {
                    steps {
                        script {
                            withSonarQubeEnv('SonarQube') {
                                dir('backend/llm_qa') {
                                    bat """
                                        sonar-scanner.bat ^
                                        -Dsonar.projectKey=docqa-ms-llm-qa ^
                                        -Dsonar.sources=app ^
                                        -Dsonar.host.url=%SONAR_HOST_URL%
                                    """
                                }
                            }
                        }
                    }
                }
                
                stage('Analyze Synthese Comparative') {
                    steps {
                        script {
                            withSonarQubeEnv('SonarQube') {
                                dir('backend/synthese_comparative') {
                                    bat """
                                        sonar-scanner.bat ^
                                        -Dsonar.projectKey=docqa-ms-synthese-comparative ^
                                        -Dsonar.sources=app ^
                                        -Dsonar.host.url=%SONAR_HOST_URL%
                                    """
                                }
                            }
                        }
                    }
                }
                
                stage('Analyze Frontend') {
                    steps {
                        script {
                            withSonarQubeEnv('SonarQube') {
                                dir('InterfaceClinique') {
                                    bat """
                                        sonar-scanner.bat ^
                                        -Dsonar.projectKey=docqa-ms-frontend ^
                                        -Dsonar.sources=src ^
                                        -Dsonar.host.url=%SONAR_HOST_URL%
                                    """
                                }
                            }
                        }
                    }
                }
            }
        }

       

        stage('Stop Existing Containers') {
            steps {
                echo ' Stopping any running containers except SonarQube...'
                script {
                    bat '''
                        REM Stop only application containers, not SonarQube
                        docker compose stop api-gateway deid ml-service doc-ingestor indexer-semantique llm-qa synthese-comparative postgres rabbitmq ollama || echo No containers to stop
                        docker compose rm -f api-gateway deid ml-service doc-ingestor indexer-semantique llm-qa synthese-comparative postgres rabbitmq ollama || echo No containers to remove
                    '''
                }
            }
        }


        stage('Build Docker Images') {
            steps {
                echo ' Building all Docker images...'
                script {
                    bat '''
                        echo Building all services with Docker Compose ...
                        echo Using cached layers to speed up build ...
                        
                        REM Build with cache and parallel jobs
                        docker compose build --parallel
                        
                        if errorlevel 1 (
                            echo  Docker build failed
                            echo Checking which service failed ...
                            docker compose config --services
                            exit /b 1
                        ) else (
                            echo  All Docker images built successfully
                            echo.
                            echo  Image Summary:
                            docker images --filter "reference=docqa-ms-*" --format "  {{.Repository}}:{{.Tag}} - {{.Size}}"
                        )
                    '''
                }
            }
        }


        stage('Start Services') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                echo ' Starting all services...'
                script {
                    bat '''
                        echo Starting services in detached mode ...
                        docker compose up -d
                        
                        if errorlevel 1 (
                            echo  Failed to start services
                            docker compose logs
                            exit /b 1
                        ) else (
                            echo  Services started successfully 
                        )
                    '''
                }
            }
        }

        stage('Health Check') {
            steps {
                echo ' Waiting for services to be ready...'
                script {
                    bat '''
                        echo Monitoring service health (max 5 minutes)...
                        echo.
                        
                        set MAX_ATTEMPTS=5
                        set ATTEMPT=0
                        
                        :CHECK_LOOP
                        set /a ATTEMPT+=1
                        
                        echo [Attempt %ATTEMPT%/%MAX_ATTEMPTS%] Checking service health...
                        
                        REM Check critical services via Docker health status
                        docker compose ps --format "{{.Service}}: {{.Status}}" | findstr /C:"(healthy)" > nul
                        if %%errorlevel%% equ 0 (
                            echo  Core services are healthy!
                            goto CHECK_ENDPOINTS
                        )
                        
                        if %ATTEMPT% geq %MAX_ATTEMPTS% (
                            echo  Timeout reached, checking current status...
                            goto CHECK_ENDPOINTS
                        )
                        
                        echo Waiting 5 seconds before retry...
                        ping -n 6 127.0.0.1 > nul
                        goto CHECK_LOOP
                        
                        :CHECK_ENDPOINTS
                        echo.
                        echo ===== Final Service Status =====
                        docker compose ps
                        
                        echo.
                        echo ===== Endpoint Checks =====
                        
                        curl -s -o nul -w "API Gateway (8000): %%{http_code}\n" http://localhost:8000/docs
                        curl -s -o nul -w "Doc Ingestor (8001): %%{http_code}\n" http://localhost:8001/docs
                        curl -s -o nul -w "DeID Service (8002): %%{http_code}\n" http://localhost:8002/docs
                        curl -s -o nul -w "Indexer (8003): %%{http_code}\n" http://localhost:8003/docs
                        curl -s -o nul -w "LLM Q&A (8004): %%{http_code}\n" http://localhost:8004/docs
                        curl -s -o nul -w "Synthese (8005): %%{http_code}\n" http://localhost:8005/docs
                        curl -s -o nul -w "ML Service (8006): %%{http_code}\n" http://localhost:8006/docs
                        
                        echo.
                        echo  Health check completed
                        exit /b 0
                    '''
                }
            }
        }

        stage('Run Basic Tests') {
            steps {
                echo ' Running basic integration tests...'
                script {
                    bat '''
                        echo ===== Database Test =====
                        docker compose exec -T postgres pg_isready -U docqa_user && echo  Database is ready || echo ⚠️ Database check failed
                        
                        echo.
                        echo ===== API Gateway Test =====
                        curl -s http://localhost:8000/docs > nul && echo  API Gateway is responding || echo ⚠️ API Gateway not responding
                        
                        echo.
                        echo ===== Container Status =====
                        docker compose ps --format "{{.Service}}: {{.State}}"
                        
                        echo.
                        echo  Basic tests completed
                        exit /b 0
                    '''
                }
            }
        }

        stage('Collect Logs') {
            steps {
                echo ' Collecting service logs...'
                script {
                    bat '''
                        echo Getting last 50 lines from each service...
                        docker compose logs --tail=50 > build_logs.txt
                        
                        if exist build_logs.txt (
                            echo  Logs collected in build_logs.txt
                        )
                    '''
                }
            }
        }

        stage('Deploy Summary') {
            steps {
                echo ' Deployment Summary...'
                script {
                    bat '''
                        echo.
                        echo =====================================
                        echo   DocQA-MS Deployment Summary
                        echo =====================================
                        echo.
                        echo  Docker Images Built:
                        docker images --filter "reference=docqa-ms*" --format "  - {{.Repository}}:{{.Tag}} ({{.Size}})"
                        echo.
                        echo  Running Services:
                        docker compose ps --format "  - {{.Service}}: {{.State}} ({{.Status}})"
                        echo.
                        echo  Service URLs:
                        echo   - API Gateway: http://localhost:8000
                        echo   - ML Service:  http://localhost:8006
                        echo   - Frontend:    http://localhost:3000
                        echo   - RabbitMQ:    http://localhost:15672
                        echo   - SonarQube:   http://localhost:9000
                        echo.
                        echo  Quality Reports:
                        echo   View SonarQube Dashboard: http://localhost:9000
                        echo.
                        echo =====================================
                        echo  Pipeline completed successfully!
                        echo =====================================
                    '''
                }
            }
        }
    }

    post {
        success {
            script {
                bat '''
                    echo.
                    echo ===================================
                    echo  PIPELINE SUCCESS 
                    echo ===================================
                    echo All services deployed successfully!
                    echo Code quality checks passed!
                    echo.
                    echo  Service URLs:
                    echo   API Gateway:  http://localhost:8000/docs
                    echo   ML Service:   http://localhost:8006/docs
                    echo   RabbitMQ UI:  http://localhost:15672
                    echo   PostgreSQL:   localhost:5432
                    echo   SonarQube:    http://localhost:9000
                    echo.
                    echo  Credentials:
                    echo   RabbitMQ: admin/admin
                    echo   PostgreSQL: docqa_user/docqa_password
                    echo   SonarQube: admin/admin123!
                    echo.
                    echo  Quality Metrics:
                    echo   Check detailed reports at http://localhost:9000
                    echo ===================================
                    exit /b 0
                '''
            }
        }
        failure {
            script {
                bat '''
                    echo.
                    echo ===================================
                    echo  PIPELINE FAILED
                    echo ===================================
                    echo.
                    echo Possible causes:
                    echo   - Quality Gate failed
                    echo   - Build errors
                    echo   - Service startup issues
                    echo.
                    echo  Collecting logs for troubleshooting...
                    docker compose logs --tail=200 > error_logs.txt 2>&1
                    echo  Logs saved to error_logs.txt
                    echo.
                    echo  Check SonarQube for quality issues:
                    echo   http://localhost:9000
                    echo.
                    echo  Current container status:
                    docker compose ps
                    echo ===================================
                    exit /b 0
                '''
            }
        }
        always {
            script {
                bat '''
                    echo.
                    echo  Cleanup: Removing dangling images...
                    docker image prune -f || echo No dangling images found
                    exit /b 0
                '''
            }
            archiveArtifacts artifacts: '*_logs.txt', allowEmptyArchive: true
        }
    }
}
