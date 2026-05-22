import os
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
API_TOKEN = os.getenv("API_TOKEN")

app = FastAPI(title="RapPanel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://painel.raptech.com.br",
        "http://localhost:5173",
        "https://mcp.raptech.com.br",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Agenda(Base):
    __tablename__ = "agenda"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    tipo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    data: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    hora: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    responsavel: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cliente: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    endereco: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pendente")
    motivo_status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    observacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    proxima_acao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_proxima_acao: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Orcamento(Base):
    __tablename__ = "orcamentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cliente: Mapped[str] = mapped_column(String(150))
    consumo_kwh: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    potencia_kwp: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    inversor: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    modulos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    marca_modulo: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    geracao_estimada_kwh: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    valor_venda: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    opcao: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    modulo_nome: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    modulo_potencia_w: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_material_dc: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    material_ac: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    instalacao: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    projeto: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    lucro: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    lucro_com_desconto_5: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    margem_percentual: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    detalhamento: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="criado")
    observacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Projeto(Base):
    __tablename__ = "projetos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    orcamento_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orcamentos.id"), nullable=True)
    cliente: Mapped[str] = mapped_column(String(150))
    status: Mapped[str] = mapped_column(String(80), default="aguardando documentação")
    observacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Estoque(Base):
    __tablename__ = "estoque"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(150))
    categoria: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    unidade: Mapped[str] = mapped_column(String(30), default="un")
    quantidade_atual: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    estoque_minimo: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    localizacao: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    observacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EstoqueMovimentacao(Base):
    __tablename__ = "estoque_movimentacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("estoque.id"))
    tipo: Mapped[str] = mapped_column(String(30))
    quantidade: Mapped[float] = mapped_column(Numeric(12, 2))
    motivo: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    responsavel: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    projeto_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projetos.id"), nullable=True)
    cliente: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    observacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Recebimento(Base):
    __tablename__ = "recebimentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cliente: Mapped[str] = mapped_column(String(150))
    valor: Mapped[float] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(50), default="a receber")
    vencimento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    origem: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    agenda_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agenda.id"), nullable=True)
    orcamento_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orcamentos.id"), nullable=True)
    projeto_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projetos.id"), nullable=True)
    cobrado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    recebido_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    observacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AgendaIn(BaseModel):
    titulo: str
    tipo: Optional[str] = None
    data: Optional[date] = None
    hora: Optional[str] = None
    responsavel: Optional[str] = None
    cliente: Optional[str] = None
    endereco: Optional[str] = None
    status: str = "pendente"
    motivo_status: Optional[str] = None
    observacao: Optional[str] = None
    proxima_acao: Optional[str] = None
    data_proxima_acao: Optional[date] = None


class AgendaUpdate(BaseModel):
    titulo: Optional[str] = None
    tipo: Optional[str] = None
    data: Optional[date] = None
    hora: Optional[str] = None
    responsavel: Optional[str] = None
    cliente: Optional[str] = None
    endereco: Optional[str] = None
    status: Optional[str] = None
    motivo_status: Optional[str] = None
    observacao: Optional[str] = None
    proxima_acao: Optional[str] = None
    data_proxima_acao: Optional[date] = None


class OrcamentoIn(BaseModel):
    cliente: str
    consumo_kwh: Optional[int] = None
    potencia_kwp: Optional[float] = None
    inversor: Optional[str] = None
    modulos: Optional[int] = None
    marca_modulo: Optional[str] = None
    geracao_estimada_kwh: Optional[int] = None
    valor_venda: Optional[float] = None
    opcao: Optional[str] = None
    modulo_nome: Optional[str] = None
    modulo_potencia_w: Optional[int] = None
    total_material_dc: Optional[float] = None
    material_ac: Optional[float] = None
    instalacao: Optional[float] = None
    projeto: Optional[float] = None
    lucro: Optional[float] = None
    lucro_com_desconto_5: Optional[float] = None
    margem_percentual: Optional[float] = None
    detalhamento: Optional[list[dict[str, Any]]] = None
    status: str = "criado"
    observacao: Optional[str] = None


class OrcamentoUpdate(BaseModel):
    cliente: Optional[str] = None
    consumo_kwh: Optional[int] = None
    potencia_kwp: Optional[float] = None
    inversor: Optional[str] = None
    modulos: Optional[int] = None
    marca_modulo: Optional[str] = None
    geracao_estimada_kwh: Optional[int] = None
    valor_venda: Optional[float] = None
    opcao: Optional[str] = None
    modulo_nome: Optional[str] = None
    modulo_potencia_w: Optional[int] = None
    total_material_dc: Optional[float] = None
    material_ac: Optional[float] = None
    instalacao: Optional[float] = None
    projeto: Optional[float] = None
    lucro: Optional[float] = None
    lucro_com_desconto_5: Optional[float] = None
    margem_percentual: Optional[float] = None
    detalhamento: Optional[list[dict[str, Any]]] = None
    status: Optional[str] = None
    observacao: Optional[str] = None


class ProjetoIn(BaseModel):
    orcamento_id: Optional[int] = None
    cliente: str
    status: str = "aguardando documentação"
    observacao: Optional[str] = None


class ProjetoUpdate(BaseModel):
    orcamento_id: Optional[int] = None
    cliente: Optional[str] = None
    status: Optional[str] = None
    observacao: Optional[str] = None


class FecharOrcamentoIn(BaseModel):
    status: str = "aguardando documentação"
    observacao: Optional[str] = None


class EstoqueIn(BaseModel):
    nome: str
    categoria: Optional[str] = None
    unidade: str = "un"
    quantidade_atual: float = 0
    estoque_minimo: float = 0
    localizacao: Optional[str] = None
    observacao: Optional[str] = None
    ativo: bool = True


class EstoqueUpdate(BaseModel):
    nome: Optional[str] = None
    categoria: Optional[str] = None
    unidade: Optional[str] = None
    quantidade_atual: Optional[float] = None
    estoque_minimo: Optional[float] = None
    localizacao: Optional[str] = None
    observacao: Optional[str] = None
    ativo: Optional[bool] = None


class EstoqueMovimentacaoIn(BaseModel):
    tipo: str
    quantidade: float
    motivo: Optional[str] = None
    responsavel: Optional[str] = None
    projeto_id: Optional[int] = None
    cliente: Optional[str] = None
    observacao: Optional[str] = None


class RecebimentoIn(BaseModel):
    cliente: str
    valor: float
    status: str = "a receber"
    vencimento: Optional[date] = None
    origem: Optional[str] = None
    agenda_id: Optional[int] = None
    orcamento_id: Optional[int] = None
    projeto_id: Optional[int] = None
    cobrado_em: Optional[datetime] = None
    recebido_em: Optional[datetime] = None
    observacao: Optional[str] = None


class RecebimentoUpdate(BaseModel):
    cliente: Optional[str] = None
    valor: Optional[float] = None
    status: Optional[str] = None
    vencimento: Optional[date] = None
    origem: Optional[str] = None
    agenda_id: Optional[int] = None
    orcamento_id: Optional[int] = None
    projeto_id: Optional[int] = None
    cobrado_em: Optional[datetime] = None
    recebido_em: Optional[datetime] = None
    observacao: Optional[str] = None


def require_token(x_api_token: Optional[str]):
    if x_api_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Token inválido")


def serialize(obj):
    data = {}
    for key, value in obj.__dict__.items():
        if key.startswith("_"):
            continue
        if isinstance(value, (date, datetime)):
            data[key] = value.isoformat()
        elif isinstance(value, Decimal):
            data[key] = float(value)
        else:
            data[key] = value
    return data


def serialize_movimentacao(movimento, nome=None, unidade=None):
    data = serialize(movimento)
    if nome is not None:
        data["nome"] = nome
        data["produto_nome"] = nome
    if unidade is not None:
        data["unidade"] = unidade
    return data


async def get_or_404(session, model, item_id: int):
    item = await session.get(model, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    return item


def apply_patch(item, payload: BaseModel):
    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(item, key, value)
    item.atualizado_em = datetime.utcnow()


def normalize_tipo_movimentacao(tipo: str):
    normalized = tipo.strip().lower()
    if normalized == "saída":
        normalized = "saida"
    if normalized not in {"entrada", "saida", "ajuste"}:
        raise HTTPException(status_code=400, detail="Tipo deve ser entrada, saida ou ajuste")
    return normalized


def normalize_status_recebimento(status: str):
    normalized = status.strip().lower()
    if normalized not in {"a receber", "cobrado", "parcial", "recebido", "atrasado", "cancelado"}:
        raise HTTPException(
            status_code=400,
            detail="Status deve ser a receber, cobrado, parcial, recebido, atrasado ou cancelado",
        )
    return normalized


@app.get("/health")
async def health(x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    return {"status": "ok"}


@app.get("/agenda")
async def listar_agenda(x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        result = await session.execute(select(Agenda).order_by(Agenda.id.desc()))
        return [serialize(item) for item in result.scalars().all()]


@app.post("/agenda")
async def criar_agenda(payload: AgendaIn, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = Agenda(**payload.model_dump())
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return serialize(item)


@app.get("/agenda/{item_id}")
async def obter_agenda(item_id: int, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = await get_or_404(session, Agenda, item_id)
        return serialize(item)


@app.patch("/agenda/{item_id}")
async def atualizar_agenda(item_id: int, payload: AgendaUpdate, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = await get_or_404(session, Agenda, item_id)
        apply_patch(item, payload)
        await session.commit()
        await session.refresh(item)
        return serialize(item)


@app.delete("/agenda/{item_id}")
async def deletar_agenda(item_id: int, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = await get_or_404(session, Agenda, item_id)
        await session.delete(item)
        await session.commit()
        return {"deleted": True, "id": item_id}


@app.get("/orcamentos")
async def listar_orcamentos(x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        result = await session.execute(select(Orcamento).order_by(Orcamento.id.desc()))
        return [serialize(item) for item in result.scalars().all()]


@app.post("/orcamentos")
async def criar_orcamento(payload: OrcamentoIn, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = Orcamento(**payload.model_dump())
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return serialize(item)


@app.get("/orcamentos/{item_id}")
async def obter_orcamento(item_id: int, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = await get_or_404(session, Orcamento, item_id)
        return serialize(item)


@app.patch("/orcamentos/{item_id}")
async def atualizar_orcamento(item_id: int, payload: OrcamentoUpdate, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = await get_or_404(session, Orcamento, item_id)
        apply_patch(item, payload)
        await session.commit()
        await session.refresh(item)
        return serialize(item)


@app.delete("/orcamentos/{item_id}")
async def deletar_orcamento(item_id: int, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = await get_or_404(session, Orcamento, item_id)
        await session.delete(item)
        await session.commit()
        return {"deleted": True, "id": item_id}


@app.post("/orcamentos/{item_id}/fechar")
async def fechar_orcamento(item_id: int, payload: FecharOrcamentoIn, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        orcamento = await get_or_404(session, Orcamento, item_id)

        result = await session.execute(select(Projeto).where(Projeto.orcamento_id == item_id))
        projeto_existente = result.scalars().first()

        if projeto_existente:
            projeto_existente.status = payload.status
            if payload.observacao is not None:
                projeto_existente.observacao = payload.observacao
            projeto_existente.atualizado_em = datetime.utcnow()
        else:
            projeto_existente = Projeto(
                orcamento_id=orcamento.id,
                cliente=orcamento.cliente,
                status=payload.status,
                observacao=payload.observacao,
            )
            session.add(projeto_existente)

        orcamento.status = "fechado"
        orcamento.atualizado_em = datetime.utcnow()

        await session.commit()
        await session.refresh(projeto_existente)
        return serialize(projeto_existente)


@app.get("/projetos")
async def listar_projetos(x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        result = await session.execute(select(Projeto).order_by(Projeto.id.desc()))
        return [serialize(item) for item in result.scalars().all()]


@app.post("/projetos")
async def criar_projeto(payload: ProjetoIn, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = Projeto(**payload.model_dump())
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return serialize(item)


@app.get("/projetos/{item_id}")
async def obter_projeto(item_id: int, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = await get_or_404(session, Projeto, item_id)
        return serialize(item)


@app.patch("/projetos/{item_id}")
async def atualizar_projeto(item_id: int, payload: ProjetoUpdate, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = await get_or_404(session, Projeto, item_id)
        apply_patch(item, payload)
        await session.commit()
        await session.refresh(item)
        return serialize(item)


@app.delete("/projetos/{item_id}")
async def deletar_projeto(item_id: int, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = await get_or_404(session, Projeto, item_id)
        await session.delete(item)
        await session.commit()
        return {"deleted": True, "id": item_id}


@app.get("/estoque")
async def listar_estoque(x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        result = await session.execute(select(Estoque).where(Estoque.ativo == True).order_by(Estoque.nome.asc()))
        return [serialize(item) for item in result.scalars().all()]


@app.post("/estoque")
async def criar_item_estoque(payload: EstoqueIn, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = Estoque(**payload.model_dump())
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return serialize(item)


@app.get("/estoque/movimentacoes")
async def listar_movimentacoes_estoque(x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        result = await session.execute(
            select(EstoqueMovimentacao, Estoque.nome, Estoque.unidade)
            .join(Estoque, Estoque.id == EstoqueMovimentacao.produto_id)
            .order_by(EstoqueMovimentacao.id.desc())
            .limit(100)
        )
        return [serialize_movimentacao(movimento, nome, unidade) for movimento, nome, unidade in result.all()]


@app.get("/estoque/{item_id}")
async def obter_item_estoque(item_id: int, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = await get_or_404(session, Estoque, item_id)
        return serialize(item)


@app.patch("/estoque/{item_id}")
async def atualizar_item_estoque(item_id: int, payload: EstoqueUpdate, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = await get_or_404(session, Estoque, item_id)
        apply_patch(item, payload)
        await session.commit()
        await session.refresh(item)
        return serialize(item)


@app.delete("/estoque/{item_id}")
async def deletar_item_estoque(item_id: int, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = await get_or_404(session, Estoque, item_id)
        item.ativo = False
        item.atualizado_em = datetime.utcnow()
        await session.commit()
        return {"deleted": True, "id": item_id}


@app.post("/estoque/{item_id}/movimentar")
async def movimentar_estoque(item_id: int, payload: EstoqueMovimentacaoIn, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = await get_or_404(session, Estoque, item_id)
        tipo = normalize_tipo_movimentacao(payload.tipo)
        quantidade = Decimal(str(payload.quantidade))

        if quantidade <= 0:
            raise HTTPException(status_code=400, detail="Quantidade deve ser maior que zero")

        saldo_atual = Decimal(str(item.quantidade_atual or 0))

        if tipo == "entrada":
            novo_saldo = saldo_atual + quantidade
        elif tipo == "saida":
            novo_saldo = saldo_atual - quantidade
            if novo_saldo < 0:
                raise HTTPException(status_code=400, detail="Saldo insuficiente para saída")
        else:
            novo_saldo = quantidade

        item.quantidade_atual = novo_saldo
        item.atualizado_em = datetime.utcnow()

        movimento = EstoqueMovimentacao(
            produto_id=item.id,
            tipo=tipo,
            quantidade=quantidade,
            motivo=payload.motivo,
            responsavel=payload.responsavel,
            projeto_id=payload.projeto_id,
            cliente=payload.cliente,
            observacao=payload.observacao,
        )
        session.add(movimento)
        await session.commit()
        await session.refresh(movimento)
        await session.refresh(item)

        return {
            "item": serialize(item),
            "movimentacao": serialize_movimentacao(movimento, item.nome, item.unidade),
        }


@app.get("/recebimentos")
async def listar_recebimentos(x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        result = await session.execute(select(Recebimento).order_by(Recebimento.id.desc()))
        return [serialize(item) for item in result.scalars().all()]


@app.post("/recebimentos")
async def criar_recebimento(payload: RecebimentoIn, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        data = payload.model_dump()
        data["status"] = normalize_status_recebimento(data["status"])
        if data["status"] in {"cobrado", "parcial"} and data.get("cobrado_em") is None:
            data["cobrado_em"] = datetime.utcnow()
        if data["status"] == "recebido" and data.get("recebido_em") is None:
            data["recebido_em"] = datetime.utcnow()

        item = Recebimento(**data)
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return serialize(item)


@app.get("/recebimentos/{item_id}")
async def obter_recebimento(item_id: int, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = await get_or_404(session, Recebimento, item_id)
        return serialize(item)


@app.patch("/recebimentos/{item_id}")
async def atualizar_recebimento(item_id: int, payload: RecebimentoUpdate, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = await get_or_404(session, Recebimento, item_id)
        changes = payload.model_dump(exclude_unset=True)
        if "status" in changes:
            changes["status"] = normalize_status_recebimento(changes["status"])
            if changes["status"] in {"cobrado", "parcial"} and item.cobrado_em is None and changes.get("cobrado_em") is None:
                changes["cobrado_em"] = datetime.utcnow()
            if changes["status"] == "recebido" and changes.get("recebido_em") is None:
                changes["recebido_em"] = datetime.utcnow()

        for key, value in changes.items():
            setattr(item, key, value)
        item.atualizado_em = datetime.utcnow()

        await session.commit()
        await session.refresh(item)
        return serialize(item)


@app.delete("/recebimentos/{item_id}")
async def deletar_recebimento(item_id: int, x_api_token: Optional[str] = Header(None)):
    require_token(x_api_token)
    async with SessionLocal() as session:
        item = await get_or_404(session, Recebimento, item_id)
        await session.delete(item)
        await session.commit()
        return {"deleted": True, "id": item_id}
