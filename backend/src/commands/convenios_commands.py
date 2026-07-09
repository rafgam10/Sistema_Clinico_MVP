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


@click.command("exportar-logos-tiss")
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=str),
    default=None,
    help="Diretório de saída das logos. Padrão: frontend/public/img/convenios.",
)
@with_appcontext
def exportar_logos_tiss_command(output_dir):
    """Exporta TBTISS.LOGOTIPO para arquivos estáticos do frontend."""

    from src.services.exportar_logos_tiss import exportar_logos_tiss

    click.echo("Exportando logos TISS dos convênios...")

    try:
        resultado = exportar_logos_tiss(output_dir=output_dir)
    except Exception as exc:
        raise click.ClickException(f"Falha ao exportar logos TISS: {exc}") from exc

    click.secho(
        (
            "\nExportação concluída:\n"
            f"  Lidos: {resultado['lidos']}\n"
            f"  Exportados: {resultado['exportados']}\n"
            f"  Sem logo: {resultado['sem_logo']}\n"
            f"  Ignorados: {resultado['ignorados']}\n"
            f"  Erros: {resultado['erros']}\n"
            f"  Saída: {resultado['output_dir']}\n"
            f"  Índice: {resultado['index_path']}"
        ),
        fg="green",
    )
