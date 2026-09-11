from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.ml.evaluation_pipeline import evaluation_pipeline
from app.models.evaluation import ModelEvaluationRecord

router = APIRouter()

@router.get("/run")
def run_model_evaluation(n_samples: int = 1000, db: Session = Depends(get_db)):
    results = evaluation_pipeline.run_evaluation(n_samples=n_samples)
    
    # Save record to DB
    comp = results["comparison_matrix"]
    rec = ModelEvaluationRecord(
        dataset_name=results["dataset_info"]["name"],
        model_name="IsolationForest-v1.2 + Security Rules",
        precision=comp["aiml_assisted"][0],
        recall=comp["aiml_assisted"][1],
        f1_score=comp["aiml_assisted"][2],
        false_positive_rate=comp["aiml_assisted"][3],
        false_negative_rate=comp["aiml_assisted"][4],
        mttd_seconds=results["soc_metrics"]["mttd_seconds"]["aiml"],
        mttr_seconds=results["soc_metrics"]["mttr_seconds"]["aiml"],
        alert_reduction_percent=results["soc_metrics"]["alert_reduction_percent"],
        metrics_json=results
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    return results

@router.get("/latest")
def get_latest_evaluation(db: Session = Depends(get_db)):
    latest = db.query(ModelEvaluationRecord).order_by(ModelEvaluationRecord.timestamp.desc()).first()
    if not latest:
        return run_model_evaluation(n_samples=1000, db=db)
    return latest.metrics_json or run_model_evaluation(n_samples=1000, db=db)
