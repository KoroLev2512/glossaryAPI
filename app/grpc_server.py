"""
gRPC сервер для работы с глоссарием терминов
"""
import grpc
from concurrent import futures
from typing import Iterator

from sqlmodel import Session, select
from grpc import ServicerContext

from .db import engine, init_db
from .models import Term

# Импортируем сгенерированные файлы из proto
try:
    from proto import glossary_pb2, glossary_pb2_grpc
except ImportError:
    # Если файлы еще не сгенерированы, создадим заглушки
    glossary_pb2 = None
    glossary_pb2_grpc = None


class GlossaryServicer(glossary_pb2_grpc.GlossaryServiceServicer if glossary_pb2_grpc else object):
    """Реализация gRPC сервиса для работы с глоссарием"""
    
    def ListTerms(self, request, context: ServicerContext):
        """Получение списка всех терминов (более тяжелый метод)"""
        with Session(engine) as session:
            query = select(Term).order_by(Term.keyword)
            
            # Поддержка пагинации
            if request.limit > 0:
                query = query.limit(request.limit)
            if request.offset > 0:
                query = query.offset(request.offset)
            
            terms = session.exec(query).all()
            total = session.exec(select(Term)).all()
            
            term_messages = [
                glossary_pb2.Term(
                    id=term.id,
                    keyword=term.keyword,
                    description=term.description,
                    source=term.source or ""
                )
                for term in terms
            ]
            
            return glossary_pb2.ListTermsResponse(
                terms=term_messages,
                total=len(total)
            )
    
    def GetTerm(self, request, context: ServicerContext):
        """Получение конкретного термина по ключевому слову (легкий метод)"""
        with Session(engine) as session:
            term = session.exec(
                select(Term).where(Term.keyword == request.keyword)
            ).first()
            
            if not term:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Term '{request.keyword}' not found")
                return glossary_pb2.GetTermResponse()
            
            return glossary_pb2.GetTermResponse(
                term=glossary_pb2.Term(
                    id=term.id,
                    keyword=term.keyword,
                    description=term.description,
                    source=term.source or ""
                )
            )
    
    def CreateTerm(self, request, context: ServicerContext):
        """Создание нового термина (средний метод)"""
        with Session(engine) as session:
            # Проверка на существование
            existing = session.exec(
                select(Term).where(Term.keyword == request.keyword)
            ).first()
            
            if existing:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(f"Term '{request.keyword}' already exists")
                return glossary_pb2.CreateTermResponse()
            
            # Создание нового термина
            term = Term(
                keyword=request.keyword,
                description=request.description,
                source=request.source if request.source else None
            )
            session.add(term)
            session.commit()
            session.refresh(term)
            
            return glossary_pb2.CreateTermResponse(
                term=glossary_pb2.Term(
                    id=term.id,
                    keyword=term.keyword,
                    description=term.description,
                    source=term.source or ""
                )
            )
    
    def UpdateTerm(self, request, context: ServicerContext):
        """Обновление существующего термина (средний метод)"""
        with Session(engine) as session:
            term = session.exec(
                select(Term).where(Term.keyword == request.keyword)
            ).first()
            
            if not term:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Term '{request.keyword}' not found")
                return glossary_pb2.UpdateTermResponse()
            
            # Обновление полей
            if request.new_keyword:
                # Проверка на конфликт
                conflict = session.exec(
                    select(Term).where(
                        Term.keyword == request.new_keyword,
                        Term.id != term.id
                    )
                ).first()
                if conflict:
                    context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                    context.set_details(f"Keyword '{request.new_keyword}' already in use")
                    return glossary_pb2.UpdateTermResponse()
                term.keyword = request.new_keyword
            
            if request.description:
                term.description = request.description
            
            if request.source:
                term.source = request.source
            
            session.add(term)
            session.commit()
            session.refresh(term)
            
            return glossary_pb2.UpdateTermResponse(
                term=glossary_pb2.Term(
                    id=term.id,
                    keyword=term.keyword,
                    description=term.description,
                    source=term.source or ""
                )
            )
    
    def DeleteTerm(self, request, context: ServicerContext):
        """Удаление термина (легкий метод)"""
        with Session(engine) as session:
            term = session.exec(
                select(Term).where(Term.keyword == request.keyword)
            ).first()
            
            if not term:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Term '{request.keyword}' not found")
                return glossary_pb2.DeleteTermResponse(success=False, message="Term not found")
            
            session.delete(term)
            session.commit()
            
            return glossary_pb2.DeleteTermResponse(
                success=True,
                message=f"Term '{request.keyword}' deleted successfully"
            )


def serve(port: int = 50051):
    """Запуск gRPC сервера"""
    # Инициализация БД
    init_db()
    
    # Создание gRPC сервера
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    if glossary_pb2_grpc:
        glossary_pb2_grpc.add_GlossaryServiceServicer_to_server(
            GlossaryServicer(), server
        )
    
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"gRPC server started on port {port}")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
