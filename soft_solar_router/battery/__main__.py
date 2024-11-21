victron_ip = "192.168.1.41"

if True:
    from datetime import time, datetime
    from soft_solar_router.battery.victron_modbus_tcp import VictronModbusTcp
    from soft_solar_router.battery.victron_modbus_tcp import BatteryData
    import logging

    if False:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(name)s %(levelname)s  %(message)s",
        )

    battery = VictronModbusTcp(host=victron_ip, max_duration=time(second=30))

    print(f"batteylife state { battery.read_battery_life_state()}")
    print(f"ess_mode { battery.read_ess_mode()}")
    # print(f"battery { battery.update(datetime.now())}")
if False:

    from pymodbus.client.sync import ModbusTcpClient

    # Configuration de l'adresse IP et du port du Victron Multiplus 2
    victron_port = 502

    # Connexion au Modbus TCP
    client = ModbusTcpClient(victron_ip, port=victron_port)

    # Fonction pour activer le mode "force charge"
    def activate_force_charge():
        try:
            # Adresse Modbus de l'enregistrement pour activer le chargeur
            register_address = 2900  # Adresse pour activer/désactiver le chargeur AC

            # Spécifier l'ID d'unité pour le Multiplus 2
            # unit_id = 228  # ID de l'unité du Multiplus 2
            unit_id = 100
            value = 6

            # Écrire une valeur dans le registre pour activer "force charge" (la valeur depend de votre appareil)
            response = client.write_register(
                register_address, value, unit=unit_id
            )  # 1 pour activer le chargeur

            if response.isError():
                print("Erreur lors de l'activation du mode 'force charge'")
                print(response)
            else:
                print("Mode 'force charge' activé avec succès")

        except Exception as e:
            print(f"Erreur : {e}")

        finally:
            # Fermer la connexion
            client.close()

    # Fonction pour changer le mode ESS
    def change_ess_mode(mode_value):
        print("write")
        try:
            # Adresse Modbus de l'enregistrement pour changer le mode ESS
            register_address = 2902  # Exemple d'adresse pour le mode ESS (à vérifier dans la documentation Victron)

            # Écrire une valeur dans le registre pour changer le mode ESS
            response = client.write_register(
                register_address, mode_value, unit=100
            )  # mode_value dépend du mode ESS souhaité

            if response.isError():
                print("Erreur lors du changement du mode ESS")
            else:
                print(f"Mode ESS changé avec succès à la valeur {mode_value}")

        except Exception as e:
            print(f"Erreur : {e}")

        finally:
            # Fermer la connexion
            client.close()

    # Appeler la fonction pour activer "force charge"
    # activate_force_charge()
    change_ess_mode(2)
