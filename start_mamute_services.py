"""Bootstrap para serviços do Mamute (monitoramento, backups, relatórios).
Mantém o loop rodando para que agendadores e WebSocket fiquem ativos.
"""
import asyncio
import logging
from mamute_advanced_system import mamute_advanced, initialize_mamute_advanced


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")
    logging.info("Iniciando serviços do Mamute (monitoramento/backup/relatórios)...")

    await initialize_mamute_advanced()
    logging.info("Serviços do Mamute ativos. Mantendo agendadores e WebSocket.")
    try:
        while True:
            await asyncio.sleep(60)
    finally:
        logging.info("Finalizando serviços do Mamute...")
        await mamute_advanced.shutdown_all_systems()
        logging.info("Serviços do Mamute finalizados.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Finalizacao graciosa ocorre no bloco finally do main
        logging.info("Interrompido pelo usuário (Ctrl+C).")
