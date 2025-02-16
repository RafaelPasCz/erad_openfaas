# Tutorial de isntalação: FaasD
### Instalando o Faasd na Raspberry Pi
O Faasd é uma re-implementação do openfaas que preza mais pela simplicidade e baixa utilização de recursos computacionais, feito especificamente para rodar em hardware como a raspberry pi, no projeto, o raspberry pi é utilizado como o servidor, e o cliente é um computador que pode invocar a função, para instalar-lo, seguir os seguintes passos:

1: No terminal, clone o repositório do faasd: git clone https://github.com/openfaas/faasd

2: Ir para o diretório do faasd: cd faasd

3: Ir para o diretório hack: cd hack

4: Executar o script de instalação: ./install.sh

5: Verificar a instalação com: systemctl status faasd e systemctl status faasd-provider

### Implantar funções no Faasd a partir de seu computadpr
Primeiramente, é necessário obter a command line interface do faasd, chamada faas-cli, para isso, execute os seguintes comandos:
curl -sLfS https://cli.openfaas.com | sh;
sudo mv faas-cli to /usr/local/bin;
 
É necessária uma senha, localizada no seguinte arquivo: /var/lib/faasd/secrets/basic-auth-password, na raspberry pi onde o faasd foi instalado, copie esse código e o transfira para o computador, também é necessário obter o endereço ip da raspberry pi na rede, em seguida, execute os seguintes comandos no terminal do computador cliente:

1: export IP=(ip raspberry pi);

2: export PASSWORD=<senha de  /var/lib/faasd/secrets/basic-auth-password>;

3: export OPENFAAS_URL=http://$IP:8080;

4: faas-cli login –password $PASSWORD;

### Crie sua função
Para criar uma função, você deve estar logado no docker em seu computador, será utilizado um exemplo de função em python, com o seguinte passo-a-passo
baixar o repositório dos templates de python, com: faas-cli template store pull python3-http-debian;

Em seguida, criar uma nova instancia do template python3-debian: faas-cli new (nome) --lang python3-debian --prefix <seu usuário do docker>

Um novo diretório, com o mesmo nome dado ao container será criado no diretório faasd, e um novo arquivo .yml, com o nome dado no comando acima, também será criado, nesse arquivo .yml, podemos customizar nosso container com alguns argumentos.
Nesse caso, usamos como exemplo o container criado para o estudo de caso:

    version: 1.0

    provider:

      name: openfaas
  
      gateway: http://127.0.0.1:8080
    
    functions:

      face-detect-thing:
  
        lang: python3-debian
    
        handler: ./face-detect-thing
    
        image: (SEU USERNAME DO DOCKER)/face-detect-thing:latest
    
        build_args:
    
          ADDITIONAL_PACKAGE: "cmake ninja-build pkg-config git gcc libgtk-3-0 libgtk-3-dev libavformat-dev libavcodec-dev libswscale-dev python3-dev"
        
          PYTHON_VERSION: 3.10
Nota: A seção ADDITIONAL_PACKAGE descreve pacotes APT a serem instalados no container, o arquivo requirements.txt, no diretorio com mesmo nome do arquivo .yml, descreve quais pacotes devem ser instalados pelo pip

### modificando dockerfile
Também é possível modificar a Dockerfile de um template, nesse exemplo iremos modificar a Dockerfile do template python3-debian, para que durante a criação do container um haarcascade para detecção facial seja baixado e guardado no deiretório onde a função é executada.
Na linha 39 da Dockerfile, adicionamos a seguinte linha

    RUN curl --output-dir /home/app/function -O https://raw.githubusercontent.com/opencv/opencv/refs/heads/master/data/haarcascades/haarcascade_frontalface_default.xml

No diretório, temos o arquivo handler.py, que contém a função a ser executada pelo faasd, o nome desse arquivo não deve ser modificado.
Para implantar a função, execute os seguintes comandos no terminal:

faas-cli publish -f <arquivo>.yml --platforms linux/arm/v7

faas-cli deploy -f <arquivo>.yml

para invocar a função, execute o seguinte comando: 

faas-cli invoke <nome da função>

Para utilizar a IU do Openfaas, em seu navegador acesse o seguinte endereço: (IP da raspberry):8080, insira admin como nome de usuario, e a senha utilizada antes para entrar
