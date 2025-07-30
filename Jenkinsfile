pipeline{
    agent any

    stages{
        stage('Checkout'){
            steps {
                git branch:'main' ,url :'https://github.com/Kamoe7/RabbitMQ-prac'
            }
        }

        stage('Build and Run Services'){
            steps{
                sh 'docker compose down'
                sh 'docker compose build'
                sh 'docker compose up -d'
            }
        }


    }

    post{
        always{
            echo "pipeline completed."
        }
    }
}