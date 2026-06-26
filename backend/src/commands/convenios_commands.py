import click

from flask.cli import with_appcontext


@click.command("importar-convenios-spdata")
@click.option(
    "--batch-size",
    default=200,
    type=click.IntRange(min=1),
    show_default=True,
    help="Quantidade de convênios processados por lote.",
)
@with_appcontext
def importar_convenios_spdata_command(batch_size):
    """Importa os convênios da TBCONVEN para o banco local."""

    from src.services.importar_convenios_spdata import importar_convenios_spdata

    click.echo("Iniciando importação dos convênios do SPDATA...")

    try:
        resultado = importar_convenios_spdata(batch_size=batch_size)
    except Exception as exc:
        raise click.ClickException(f"Falha ao importar convênios: {exc}") from exc

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
