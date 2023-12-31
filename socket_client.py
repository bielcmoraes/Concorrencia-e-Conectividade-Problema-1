import json
import socket
import os

def read_products(rfid_socket):
    try:
        while True:
            ids_string = rfid_socket.recv(1024).decode("utf-8")
            if ids_string:
                string = ids_string.strip("[]")
                substrings = string.split(", ")
                id_list = [s.replace("'", "") for s in substrings]
                return id_list
            break
    except ConnectionAbortedError:
        print("\nRFID desconectado")
        print("Tente novamente")
    except:
        pass

def shipping_with_confirmation(client_socket, json_message):
    try:
        json_message = json.dumps(json_message)
        client_socket.sendall(json_message.encode("utf-8"))
        data_recv = client_socket.recv(1024).decode()
        data_recv_decode = json.loads(data_recv)
        return data_recv_decode
    except ConnectionAbortedError:
        print("\nCaixa desconectado")
        print("Tente conectar-se novamente")
        exit()

def handle_conection(host, port):

    conection_socket = socket.socket()
    conection_socket.connect((host, port))
    print("Conectado ao servidor em", host, "porta", port)
    return conection_socket

def main():
    socket_port = int(os.environ.get('PORT_SOCKET_SERVER', 3322))
    rfid_port = int(os.environ.get('PORT_RFID', 1234))
    rfid_host = os.environ.get('HOST_RFID', '172.16.103.0')
    socket_host = input("Digite o ip do servidor: ")

    try:
        try:
            client_socket = handle_conection(socket_host, socket_port)
        except:
            print("\nErro na conexão")
            print("Reinicie e tente novamente")
            exit()

        while True:
            print("\nMenu do Supermercado:")
            print("1. Iniciar uma compra")
            print("2. Sair")

            escolha_menu_principal = input("Digite 1 para iniciar uma compra ou 2 para sair: ")

            if escolha_menu_principal == "1":
                shoppingList = {"products": [], "amout": 0.00}

                while True:
                    print("\nOpções de Compra:")
                    print("1. Digitar o ID manualmente")
                    print("2. Pegar do leitor RFID")
                    print("3. Finalizar compra e retornar ao menu anterior")

                    escolha_opcoes_compra = input("Escolha uma opção de compra (1/2/3): ")

                    if escolha_opcoes_compra == "1":
                        product_id = input("Id: ")
                        product = shipping_with_confirmation(client_socket, {"id": product_id})

                        product_not_exists = product.get("error")
                        if product_not_exists is not None:
                            print(product_not_exists)
                        else:
                            product_name = product.get("nome")
                            shoppingList["products"].append({"id": product_id, "nome": product_name})
                            shoppingList["amout"] += product.get("preco", 0.0)
                            print(product)
                        pass

                    elif escolha_opcoes_compra == "2":

                        try:
                            rfid_socket = handle_conection(rfid_host, rfid_port)
                            ids_list = read_products(rfid_socket)
                            try:
                                for product_id in ids_list:
                                    print(product_id)
                                    product = shipping_with_confirmation(client_socket, {"id": product_id})
                                    product_not_exists = product.get("error")
                                    if product_not_exists is not None:
                                        print(product_not_exists)
                                    else:
                                        product_name = product.get("nome")
                                        shoppingList["products"].append({"id": product_id, "nome": product_name})
                                        shoppingList["amout"] += product.get("preco", 0.0)
                                        print(product_name)
                                    pass
                            except Exception as e:
                                print("Error: ", e)
                            rfid_socket.close()
                            pass
                        except TimeoutError:
                            print("\nLeitor RFID indisponível")
                            pass

                    elif escolha_opcoes_compra == "3":
                        purchase_confirmation = shipping_with_confirmation(client_socket, shoppingList)
                        print(purchase_confirmation)
                        break

                    else:
                        print("\nOpção inválida. Por favor, escolha uma opção válida.")

            elif escolha_menu_principal == "2":
                try:
                    print("\nFechando caixa. Até logo!")
                    json_message = json.dumps({"message": "disconnect"})
                    client_socket.sendall(json_message.encode("utf-8"))
                    client_socket.close()
                    break
                except ConnectionAbortedError:
                    print("\nCaixa desconectado")
                    print("Tente conectar-se novamente")
                    exit()

            else:
                print("\nOpção inválida. Por favor, escolha uma opção válida.")
    
    except ConnectionResetError:
        print("\nServidor temporariamente indisponível")
        print("Tente conectar-se novamente")
        exit()
    
    except ConnectionAbortedError:
        print("\nServidor temporariamente indisponível")
        print("Tente conectar-se novamente")
        exit()

if __name__ == "__main__":
    main()