import React from 'react';
import { motion } from 'framer-motion';
import { BarChart, Target, TrendingUp, TrendingDown, Minus } from 'lucide-react';

export interface CoverageMetrics {
  lines: { pct: number; covered: number; total: number };
  statements: { pct: number; covered: number; total: number };
  functions: { pct: number; covered: number; total: number };
  branches: { pct: number; covered: number; total: number };
}

export interface CoverageData {
  total: CoverageMetrics;
  files?: Record<string, CoverageMetrics>;
  timestamp?: string;
}

interface CoverageVisualizationProps {
  coverage: CoverageData | null;
  showFileBreakdown?: boolean;
  compact?: boolean;
  className?: string;
}

interface CoverageGaugeProps {
  label: string;
  value: number;
  threshold: number;
  covered: number;
  total: number;
  size?: 'sm' | 'md' | 'lg';
  showTrend?: boolean;
  previousValue?: number;
}

const CoverageGauge: React.FC<CoverageGaugeProps> = ({
  label,
  value,
  threshold,
  covered,
  total,
  size = 'md',
  showTrend = false,
  previousValue
}) => {
  const sizeConfig = {
    sm: { size: 60, strokeWidth: 4, fontSize: 'text-xs' },
    md: { size: 80, strokeWidth: 6, fontSize: 'text-sm' },
    lg: { size: 100, strokeWidth: 8, fontSize: 'text-base' }
  };

  const config = sizeConfig[size];
  const radius = (config.size - config.strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (value / 100) * circumference;

  // Color coding based on thresholds
  const getColor = (percentage: number) => {
    if (percentage >= 90) return 'text-emerald-500 border-emerald-500';
    if (percentage >= threshold) return 'text-green-500 border-green-500';
    if (percentage >= threshold - 20) return 'text-yellow-500 border-yellow-500';
    return 'text-red-500 border-red-500';
  };

  const getStrokeColor = (percentage: number) => {
    if (percentage >= 90) return '#10b981'; // emerald-500
    if (percentage >= threshold) return '#22c55e'; // green-500
    if (percentage >= threshold - 20) return '#eab308'; // yellow-500
    return '#ef4444'; // red-500
  };

  const getTrend = () => {
    if (!showTrend || previousValue === undefined) return null;
    const diff = value - previousValue;
    if (Math.abs(diff) < 0.1) return <Minus className="w-3 h-3 text-gray-400" />;
    return diff > 0 
      ? <TrendingUp className="w-3 h-3 text-green-500" />
      : <TrendingDown className="w-3 h-3 text-red-500" />;
  };

  return (
    <div className="relative flex flex-col items-center p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-all duration-200">
      {/* SVG Gauge */}
      <div className="relative">
        <svg
          width={config.size}
          height={config.size}
          className="transform -rotate-90"
        >
          {/* Background circle */}
          <circle
            cx={config.size / 2}
            cy={config.size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={config.strokeWidth}
            fill="none"
            className="text-gray-200 dark:text-gray-700"
          />
          {/* Progress circle */}
          <motion.circle
            cx={config.size / 2}
            cy={config.size / 2}
            r={radius}
            stroke={getStrokeColor(value)}
            strokeWidth={config.strokeWidth}
            fill="none"
            strokeLinecap="round"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1, ease: "easeInOut" }}
          />
        </svg>
        
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className={`font-bold ${config.fontSize} ${getColor(value)}`}>
            {value.toFixed(1)}%
          </div>
          {showTrend && (
            <div className="flex items-center gap-1 mt-1">
              {getTrend()}
            </div>
          )}
        </div>
      </div>

      {/* Label and stats */}
      <div className="text-center mt-3">
        <div className="font-medium text-gray-700 dark:text-gray-300 text-sm">
          {label}
        </div>
        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          {covered} / {total}
        </div>
        <div className={`text-xs mt-1 px-2 py-1 rounded-full border ${getColor(value)} bg-opacity-10 dark:bg-opacity-20`}>
          {value >= 90 ? 'Excellent' : 
           value >= threshold ? 'Good' : 
           value >= threshold - 20 ? 'Fair' : 'Poor'}
        </div>
      </div>
    </div>
  );
};

const FileBreakdown: React.FC<{ files: Record<string, CoverageMetrics> }> = ({ files }) => {
  const fileEntries = Object.entries(files).slice(0, 10); // Show top 10 files

  return (
    <div className="mt-6">
      <h4 className="text-lg font-semibold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
        <BarChart className="w-5 h-5 text-blue-500" />
        File Coverage Breakdown
      </h4>
      
      <div className="overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-900/50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                File
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Lines
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Functions
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Branches
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {fileEntries.map(([filename, metrics], index) => (
              <motion.tr
                key={filename}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="hover:bg-gray-50 dark:hover:bg-gray-700/50"
              >
                <td className="px-4 py-3">
                  <div className="text-sm font-mono text-gray-900 dark:text-white truncate max-w-xs" title={filename}>
                    {filename.split('/').pop()}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 truncate max-w-xs">
                    {filename.includes('/') ? filename.split('/').slice(0, -1).join('/') : ''}
                  </div>
                </td>
                <td className="px-4 py-3 text-center">
                  <div className="flex items-center justify-center">
                    <div className={`text-sm font-medium ${
                      metrics.lines.pct >= 80 ? 'text-green-600 dark:text-green-400' :
                      metrics.lines.pct >= 60 ? 'text-yellow-600 dark:text-yellow-400' :
                      'text-red-600 dark:text-red-400'
                    }`}>
                      {metrics.lines.pct.toFixed(1)}%
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3 text-center">
                  <div className="flex items-center justify-center">
                    <div className={`text-sm font-medium ${
                      metrics.functions.pct >= 80 ? 'text-green-600 dark:text-green-400' :
                      metrics.functions.pct >= 60 ? 'text-yellow-600 dark:text-yellow-400' :
                      'text-red-600 dark:text-red-400'
                    }`}>
                      {metrics.functions.pct.toFixed(1)}%
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3 text-center">
                  <div className="flex items-center justify-center">
                    <div className={`text-sm font-medium ${
                      metrics.branches.pct >= 70 ? 'text-green-600 dark:text-green-400' :
                      metrics.branches.pct >= 50 ? 'text-yellow-600 dark:text-yellow-400' :
                      'text-red-600 dark:text-red-400'
                    }`}>
                      {metrics.branches.pct.toFixed(1)}%
                    </div>
                  </div>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export const CoverageVisualization: React.FC<CoverageVisualizationProps> = ({
  coverage,
  showFileBreakdown = false,
  compact = false,
  className = ''
}) => {
  if (!coverage) {
    return (
      <div className={`flex flex-col items-center justify-center p-8 text-center ${className}`}>
        <Target className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
        <h3 className="text-lg font-medium text-gray-500 dark:text-gray-400 mb-2">
          No Coverage Data
        </h3>
        <p className="text-sm text-gray-400 dark:text-gray-500">
          Run tests with coverage to see detailed metrics
        </p>
      </div>
    );
  }

  const { total } = coverage;
  const gaugeSize = compact ? 'sm' : 'md';

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Target className="w-6 h-6 text-blue-500" />
          <h3 className="text-xl font-semibold text-gray-800 dark:text-white">
            Coverage Analysis
          </h3>
        </div>
        {coverage.timestamp && (
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Updated {new Date(coverage.timestamp).toLocaleTimeString()}
          </div>
        )}
      </div>

      {/* Coverage Gauges */}
      <div className={`grid gap-4 ${compact ? 'grid-cols-4' : 'grid-cols-2 lg:grid-cols-4'}`}>
        <CoverageGauge
          label="Lines"
          value={total.lines.pct}
          threshold={80}
          covered={total.lines.covered}
          total={total.lines.total}
          size={gaugeSize}
        />
        <CoverageGauge
          label="Statements"
          value={total.statements.pct}
          threshold={80}
          covered={total.statements.covered}
          total={total.statements.total}
          size={gaugeSize}
        />
        <CoverageGauge
          label="Functions"
          value={total.functions.pct}
          threshold={80}
          covered={total.functions.covered}
          total={total.functions.total}
          size={gaugeSize}
        />
        <CoverageGauge
          label="Branches"
          value={total.branches.pct}
          threshold={70}
          covered={total.branches.covered}
          total={total.branches.total}
          size={gaugeSize}
        />
      </div>

      {/* Overall Score Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-6 rounded-lg border border-blue-200 dark:border-blue-800"
      >
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-lg font-semibold text-gray-800 dark:text-white">
              Overall Coverage Score
            </h4>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Combined average across all metrics
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
              {((total.lines.pct + total.statements.pct + total.functions.pct + total.branches.pct) / 4).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {((total.lines.pct + total.statements.pct + total.functions.pct + total.branches.pct) / 4) >= 80 
                ? 'Excellent' 
                : ((total.lines.pct + total.statements.pct + total.functions.pct + total.branches.pct) / 4) >= 60 
                ? 'Good' 
                : 'Needs Improvement'
              }
            </div>
          </div>
        </div>
      </motion.div>

      {/* File Breakdown */}
      {showFileBreakdown && coverage.files && Object.keys(coverage.files).length > 0 && (
        <FileBreakdown files={coverage.files} />
      )}
    </div>
  );
};

export default CoverageVisualization;