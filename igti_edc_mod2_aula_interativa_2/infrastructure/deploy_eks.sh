eksctl create cluster \
    --managed --alb-ingress-access --node-private-networking --full-ecr-access --asg-access --name=kubeedcxp \ 
    --instance-types=m6i.xlarge \
    --region=us-east-1 \
    --nodes-min=2 --nodes-max=3  \
    --nodegroup-name=ng-kubeedcxp
    
