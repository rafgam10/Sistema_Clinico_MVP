import click

from flask.cli import with_appcontext

@click.command("importar-exames-spdata")
@click.option(
    "--batch-size",
    default=200,
    type=click.IntRange(min=1),
    show_default=True,
    help="Quantidade de exames processados por lote.",
)
@with_appcontext
def importar_exames_spdata_command(batch_size):
    """Importa os exames da SITABPRO para o banco local."""

    from src.services.importar_exames_spdata import importar_exames_spdata

    click.echo("Iniciando importação dos exames do SPDATA...")

    resultado = importar_exames_spdata(
        batch_size=batch_size,
    )

    click.secho(
        (
            "\nImportação concluída:\n"
            f"  Lidos: {resultado['lidos']}\n"
            f"  Criados: {resultado['criados']}\n"
            f"  Atualizados: {resultado['atualizados']}\n"
            f"  Erros: {resultado['erros']}"
        ),
        fg="green",
    )
