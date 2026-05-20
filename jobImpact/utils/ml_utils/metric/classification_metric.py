import sys
from sklearn.metrics import f1_score, precision_score, recall_score
from jobImpact.exception.exception import JobImpactException

from jobImpact.entity.artifact_entity import ClassificationMetricArtifact

def get_classification_score(y_true, y_pred) -> ClassificationMetricArtifact:
    try:
        # Crucial change: Added average="weighted" for multi-class support
        model_f1_score = f1_score(y_true, y_pred, average="weighted")
        model_recall_score = recall_score(y_true, y_pred, average="weighted")
        model_precision_score = precision_score(y_true, y_pred, average="weighted")

        classification_metric = ClassificationMetricArtifact(
            f1_score=model_f1_score,
            precision_score=model_precision_score,
            recall_score=model_recall_score
        )
        return classification_metric
    except Exception as e:
        raise JobImpactException(e, sys)