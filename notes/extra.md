##So here's begin the note writing here
##The note here will emphasize on differentiate the usage of deployment and also the services.yaml

# Deployment.yaml
So basically this .yaml written is to manage the how your application was running (especially for like lifecycle) 
EXAMPLE: Manages Pods (creating,scaling,update)
TARGET: Docker images and also the replica count

# Services.yaml
How people or other application finds each other and talk to it (its networking)...
EXAMPLE: Exposes Pods (networking, load balancing)
TARGET: Ports or Selectors to find Pods
                                                                                                                                                                
**Why this is no longer "Vibe-Code"**
Look at what you’ve actually created here. You’ve implemented Idempotency—a core SRE concept.
Definition: An operation is "idempotent" if you can run it multiple times and it always results in the same state without breaking.
By adding the docker rm -f line before the run command, you ensure that even if a developer runs your tool 100 times, it won't crash because the "name is already taken." You are managing the state of the system automatically.
                                                                                                                                                                