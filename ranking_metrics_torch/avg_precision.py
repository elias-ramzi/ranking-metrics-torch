import torch

from ranking_metrics_torch.common import _check_inputs
from ranking_metrics_torch.common import _extract_topk
from ranking_metrics_torch.common import _create_output_placeholder
from ranking_metrics_torch.common import _mask_with_nans
from ranking_metrics_torch.precision_recall import precision_at


def avg_precision_at(
    ks: torch.Tensor, scores: torch.Tensor, labels: torch.Tensor,
    at_R=False,
    embeddings_come_from_same_source: bool = False,
) -> torch.Tensor:
    """Compute average precision at K for provided cutoffs

    Args:
        ks (torch.Tensor or list): list of cutoffs
        scores (torch.Tensor): 2-dim tensor of predicted item scores
        labels (torch.Tensor): 2-dim tensor of true item labels

    Returns:
        torch.Tensor: list of average precisions at cutoffs
    """
    ks, scores, labels = _check_inputs(ks, scores, labels)
    topk_scores, _, topk_labels = _extract_topk(ks, scores, labels, embeddings_come_from_same_source=embeddings_come_from_same_source)
    avg_precisions = _create_output_placeholder(scores, ks)

    # Compute average precisions at K
    num_relevant = torch.sum(labels, dim=1)
    max_k = ks.max().item()

    precisions = precision_at(1 + torch.arange(max_k), topk_scores, topk_labels)
    rel_precisions = precisions * topk_labels

    for index, k in enumerate(ks):
        normalize = num_relevant if at_R else num_relevant.clamp(min=1, max=k)
        total_prec = rel_precisions[:, : int(k)].sum(dim=1)
        avg_precisions[:, index] = total_prec / normalize

    return _mask_with_nans(avg_precisions, labels)
