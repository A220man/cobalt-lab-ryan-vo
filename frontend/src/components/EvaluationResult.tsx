import type { Evaluation } from '../types';

interface Props {
  evaluation: Evaluation;
}

export default function EvaluationResult({ evaluation }: Props) {
  const score = Math.round(evaluation.overall_score * 100);

  const dimensionEntries = Object.entries(evaluation.dimension_scores).sort(
    ([, a], [, b]) => b - a,
  );

  return (
    <div className="evaluation-result">
      <div className="score-header">
        <h3>Fit Score: {score}%</h3>
      </div>

      <table className="dimension-table">
        <thead>
          <tr>
            <th>Dimension</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {dimensionEntries.map(([dim, val]) => (
            <tr key={dim}>
              <td>{dim}</td>
              <td>{Math.round(val * 100)}%</td>
            </tr>
          ))}
        </tbody>
      </table>

      {evaluation.skill_overlap.length > 0 && (
        <p className="skill-overlap">
          <strong>Skills matched:</strong>{' '}
          {evaluation.skill_overlap.join(', ')}
        </p>
      )}

      {evaluation.dealbreaker_hits.length > 0 && (
        <p className="dealbreaker-hits">
          <strong>Dealbreakers hit:</strong>{' '}
          {evaluation.dealbreaker_hits.join(', ')}
        </p>
      )}

      {evaluation.explanation && (
        <p className="explanation">{evaluation.explanation}</p>
      )}
    </div>
  );
}