# Classify-images-of-clothing
docker 创建cassandra  
docker network create some-network  
docker run --name Daniel-cassandra --network some-network -p 9042:9042 -d cassandra  
docker run -it --network some-network --rm cassandra cqlsh Daniel-cassandra  
##annaconda配置环境  
conda env create -f environment.yml  # 改为你保存的environment.yml路径  
把python编译器设置为新的虚拟环境  
运行app.py  
