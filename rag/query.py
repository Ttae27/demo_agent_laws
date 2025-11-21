from model import get_embedding_model
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from typing import Dict, Union

@tool
def query_rag(query_text: str): 
    """
    Retrieve relevant documents from the database.
    """
    
    embeddings = get_embedding_model()
    sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")

    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        sparse_embedding=sparse_embeddings,
        retrieval_mode=RetrievalMode.HYBRID,
        collection_name="my_documents",
        url="http://localhost:6333",
        vector_name="dense",
        sparse_vector_name="sparse"
    )

    results = vector_store.similarity_search(query_text, k=6)

    for res in results:
        print('-'*100)
        print(f"* {res.page_content}")

    full_context = "\n\n---\n\n".join([str(doc.page_content) for doc in results])
    return full_context

@tool
def check_budget_discipline_s20(
    total_budget: float,
    investment_budget: float,
    deficit_amount: float = 0
) -> Dict[str, Union[bool, str, float]]:
    """
    Calculates compliance with Section 20 (1) of the State Fiscal and Financial Discipline Act B.E. 2561.

    Args:
        total_budget (float): วงเงินงบประมาณรายจ่ายประจำปีทั้งหมด (Total Annual Budget)
        investment_budget (float): งบประมาณรายจ่ายลงทุน (Capital/Investment Expenditure)
        deficit_amount (float): วงเงินส่วนที่ขาดดุลงบประมาณ (Budget Deficit Amount). Default is 0 if balanced budget.

    Returns:
        Dict: Contains pass/fail status, calculations, and explanation.
    """

    investment_ratio = (investment_budget / total_budget) * 100
    is_ratio_pass = investment_ratio >= 20.0

    is_deficit_pass = investment_budget >= deficit_amount

    is_compliant = is_ratio_pass and is_deficit_pass

    explanation = []
    if not is_ratio_pass:
        explanation.append(f"ไม่ผ่านเกณฑ์ที่ 1: สัดส่วนงบลงทุนอยู่ที่ {investment_ratio:.2f}% (กฎหมายกำหนดต้องไม่น้อยกว่า 20%)")
    else:
        explanation.append(f"ผ่านเกณฑ์ที่ 1: สัดส่วนงบลงทุนอยู่ที่ {investment_ratio:.2f}%")

    if not is_deficit_pass:
        explanation.append(f"ไม่ผ่านเกณฑ์ที่ 2: งบลงทุน ({investment_budget:,.2f}) น้อยกว่าการขาดดุล ({deficit_amount:,.2f})")
    else:
        explanation.append(f"ผ่านเกณฑ์ที่ 2: งบลงทุนมากกว่าหรือเท่ากับการขาดดุล")

    return {
        "compliant": is_compliant,
        "investment_ratio_percent": investment_ratio,
        "gap_investment_deficit": investment_budget - deficit_amount,
        "message": " และ ".join(explanation)
    }