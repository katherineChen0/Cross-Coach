import React from 'react';

type Insight = {
  id: string;
  user_id: string;
  week_start: string;
  summary?: string | null;
  correlations?: Record<string, number> | null;
};

type InsightsFeedProps = {
  insights: Insight[];
};

const InsightsFeed: React.FC<InsightsFeedProps> = ({ insights }) => {
  const formatCorrelation = (correlation: number) => {
    const absValue = Math.abs(correlation);
    let strength = '';
    let color = '';

    if (absValue >= 0.7) {
      strength = 'Strong';
      color = 'text-red-600';
    } else if (absValue >= 0.4) {
      strength = 'Moderate';
      color = 'text-orange-600';
    } else if (absValue >= 0.2) {
      strength = 'Weak';
      color = 'text-yellow-600';
    } else {
      strength = 'Very Weak';
      color = 'text-gray-600';
    }

    const direction = correlation > 0 ? 'positive' : 'negative';
    return { strength, direction, color, value: correlation };
  };

  const generateAICoachInsight = (insight: Insight) => {
    const correlations = insight.correlations || {};
    const topCorrelations = Object.entries(correlations)
      .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
      .slice(0, 3);

    if (topCorrelations.length === 0) {
      return {
        title: "Keep up the great work!",
        message: "You're building consistent habits. Consider setting specific goals for areas you'd like to improve.",
        type: "motivation"
      };
    }

    const [strongestCorrelation] = topCorrelations;
    const [metric, correlation] = strongestCorrelation;
    const { strength, direction } = formatCorrelation(correlation);

    if (Math.abs(correlation) >= 0.6) {
      return {
        title: `Strong ${direction} correlation detected`,
        message: `Your ${metric.replace(/_/g, ' ')} shows a ${strength.toLowerCase()} ${direction} relationship with other activities. This could indicate a key factor in your routine.`,
        type: "correlation"
      };
    }

    return {
      title: "Patterns emerging",
      message: "We're starting to see some interesting patterns in your data. Keep logging consistently to unlock more insights!",
      type: "pattern"
    };
  };

  if (insights.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Insights Feed</h3>
        <div className="text-center py-8 text-gray-500">
          <div className="mb-4">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <p>No insights available yet.</p>
          <p className="text-sm">Continue logging your activities to receive personalized insights!</p>
        </div>
      </div>
    );
  }

  const latestInsight = insights[0];
  const aiInsight = generateAICoachInsight(latestInsight);

  return (
    <div className="space-y-6">
      {/* AI Coach Insight */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl shadow-lg p-6 border border-blue-100">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
          </div>
          <div className="flex-1">
            <h4 className="text-lg font-semibold text-gray-900 mb-2">{aiInsight.title}</h4>
            <p className="text-gray-700 mb-3">{aiInsight.message}</p>
            <div className="text-sm text-gray-500">
              Week of {new Date(latestInsight.week_start).toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>

      {/* Weekly Summary */}
      {latestInsight.summary && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Weekly Summary</h4>
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-700 whitespace-pre-wrap">{latestInsight.summary}</p>
          </div>
        </div>
      )}

      {/* Correlation Insights */}
      {latestInsight.correlations && Object.keys(latestInsight.correlations).length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Key Correlations</h4>
          <div className="grid gap-3">
            {Object.entries(latestInsight.correlations)
              .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
              .slice(0, 5)
              .map(([metric, correlation]) => {
                const { strength, direction, color, value } = formatCorrelation(correlation);
                return (
                  <div key={metric} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <span className="font-medium text-gray-900">
                        {metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                      <span className={`ml-2 text-sm ${color}`}>
                        {strength} {direction} correlation
                      </span>
                    </div>
                    <span className="text-sm font-mono text-gray-600">
                      {value.toFixed(3)}
                    </span>
                  </div>
                );
              })}
          </div>
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl shadow-lg p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">
            {insights.length}
          </div>
          <div className="text-sm text-gray-600">Weeks Analyzed</div>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-600">
            {latestInsight.correlations ? Object.keys(latestInsight.correlations).length : 0}
          </div>
          <div className="text-sm text-gray-600">Patterns Found</div>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-4 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {latestInsight.correlations 
              ? Object.values(latestInsight.correlations).filter(c => Math.abs(c) >= 0.4).length 
              : 0}
          </div>
          <div className="text-sm text-gray-600">Strong Correlations</div>
        </div>
      </div>
    </div>
  );
};

export default InsightsFeed; 