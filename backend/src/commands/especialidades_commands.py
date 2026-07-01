import click

from flask.cli import with_appcontext


@click.command("importar-especialidades-spdata")
@click.option(
    "--batch-size",
    default=200,
    type=click.IntRange(min=1),
    show_default=True,
    help="Quantidade de especialidades processadas por lote.",
)
@with_appcontext
def importar_especialidades_spdata_command(batch_size):
    """Importa as especialidades da TBESPEC para o banco local."""

    from src.services.importar_especialidades_spdata import importar_especialidades_spdata

    click.echo("Iniciando importação das especialidades do SPDATA...")

    try:
        resultado = importar_especialidades_spdata(batch_size=batch_size)
    except Exception as exc:
        raise click.ClickException(f"Falha ao importar especialidades: {exc}") from exc

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
