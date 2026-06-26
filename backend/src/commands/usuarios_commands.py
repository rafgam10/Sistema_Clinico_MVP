import click

from flask.cli import with_appcontext

from src.models.usuario_model import Usuario
from src.settings.extensions import db


@click.command("registrar-recepcao")
@click.option("--nome-completo", prompt=True, help="Nome completo do usuário da recepção.")
@click.option("--documento", prompt=True, help="CPF/CNPJ do usuário da recepção.")
@click.option("--email", prompt=True, help="E-mail usado no login.")
@click.option(
    "--senha",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Senha inicial do usuário da recepção.",
)
@click.option(
    "--atualizar",
    is_flag=True,
    help="Atualiza o usuário existente pelo e-mail, se ele já existir.",
)
@with_appcontext
def registrar_recepcao_command(nome_completo, documento, email, senha, atualizar):
    """Cria um usuário local com role recepcao."""

    nome_completo = (nome_completo or "").strip()
    documento = (documento or "").strip()
    email = (email or "").strip().lower()

    if not nome_completo:
        raise click.ClickException("Informe --nome-completo.")
    if not documento:
        raise click.ClickException("Informe --documento.")
    if not email:
        raise click.ClickException("Informe --email.")
    if not senha:
        raise click.ClickException("Informe --senha.")

    usuario = db.session.query(Usuario).filter(Usuario.email == email).first()

    if usuario and not atualizar:
        raise click.ClickException(
            "Já existe um usuário com esse e-mail. Use --atualizar para alterar."
        )

    try:
        if usuario is None:
            usuario = Usuario(
                nome_completo=nome_completo,
                cnpj_cpf=documento,
                email=email,
                senha=senha,
                role="recepcao",
            )
            db.session.add(usuario)
            acao = "criado"
        else:
            usuario.nome_completo = nome_completo
            usuario.cnpj_cpf = documento
            usuario.senha = senha
            usuario.role = "recepcao"
            acao = "atualizado"

        db.session.commit()

    except Exception as exc:
        db.session.rollback()
        raise click.ClickException(f"Falha ao registrar recepção: {exc}") from exc

    click.secho("Usuário de recepção registrado com sucesso.", fg="green")
    click.echo(f"  usuario_id: {usuario.id} ({acao})")
    click.echo(f"  nome: {usuario.nome_completo}")
    click.echo(f"  email: {usuario.email}")
    click.echo(f"  role: {usuario.role}")
