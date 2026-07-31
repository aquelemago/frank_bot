from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path


def render_attendant_email(
    attendant: str,
    exported_at: datetime,
    row_count: int,
    no_interaction_days: int,
) -> str:
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1f2933; line-height: 1.5;">
        <p>Ol&aacute;, {html.escape(attendant)}.</p>

        <p>
          Segue em anexo a rela&ccedil;&atilde;o de chamados vinculados ao seu atendimento
          que est&atilde;o sem qualquer intera&ccedil;&atilde;o h&aacute; {no_interaction_days}
          dias ou mais.
        </p>

        <p>
          Conforme observado, h&aacute; chamados pendentes que necessitam de revis&atilde;o
          priorit&aacute;ria, principalmente nos casos em que o cliente aguarda retorno ou
          atualiza&ccedil;&atilde;o do andamento. Refor&ccedil;amos a import&acirc;ncia de avaliar
          os chamados listados o quanto antes, evitando impacto no atendimento.
        </p>

        <p>
          <strong>Total de chamados no anexo:</strong> {row_count}<br>
          <strong>Data e hora da exporta&ccedil;&atilde;o:</strong> {exported_at:%d/%m/%Y %H:%M:%S}
        </p>

        <p>
          Esta &eacute; uma mensagem autom&aacute;tica da rotina de apoio do Soft4.
        </p>
      </body>
    </html>
    """


def render_test_email(sent_at: datetime) -> str:
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1f2933; line-height: 1.5;">
        <p>Ola.</p>

        <p>
          Este e um e-mail de teste da automacao Soft4/Mainhardt.
        </p>

        <p>
          Se voce recebeu esta mensagem, as configuracoes SMTP estao funcionando
          para envio pela rotina.
        </p>

        <p>
          <strong>Data e hora do teste:</strong> {sent_at:%d/%m/%Y %H:%M:%S}
        </p>
      </body>
    </html>
    """


def render_dry_run_success_email(
    exported_at: datetime,
    simulated_individual_emails: int,
    queue_dir: Path,
) -> str:
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1f2933; line-height: 1.5;">
        <p>Ola.</p>

        <p>
          O dry-run da automacao Soft4/Mainhardt foi concluido com sucesso.
        </p>

        <p>
          Nenhum e-mail de atendimento foi enviado para atendentes ou gestora.
          A rotina apenas simulou a execucao real e validou a fila gerada.
        </p>

        <p>
          <strong>E-mails individuais simulados:</strong> {simulated_individual_emails}<br>
          <strong>Relatorio gerencial simulado:</strong> sim<br>
          <strong>Data e hora da exportacao:</strong> {exported_at:%d/%m/%Y %H:%M:%S}<br>
          <strong>Fila gerada:</strong> {html.escape(str(queue_dir))}
        </p>
      </body>
    </html>
    """


def render_manager_report_email(
    manager_name: str,
    exported_at: datetime,
    no_interaction_days: int,
    total_attendants: int,
    total_rows: int,
    sections: str,
) -> str:
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1f2933; line-height: 1.5;">
        <p>Ola, {html.escape(manager_name)}.</p>

        <p>
          Segue o relatorio consolidado dos chamados sem interacao do atendente ha
          {no_interaction_days} dias ou mais, organizado por atendente.
        </p>

        <p>
          <strong>Total de atendentes no relatorio:</strong> {total_attendants}<br>
          <strong>Total de chamados:</strong> {total_rows}<br>
          <strong>Data e hora da exportacao:</strong> {exported_at:%d/%m/%Y %H:%M:%S}
        </p>

        {sections}

        <p>
          O CSV completo da exportacao tambem segue em anexo para conferencia ou filtro.
        </p>

        <p>
          Esta e uma mensagem automatica da rotina de apoio do Soft4.
        </p>
      </body>
    </html>
    """
