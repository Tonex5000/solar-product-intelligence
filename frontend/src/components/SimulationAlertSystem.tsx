import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  AlertTriangle, 
  XCircle, 
  Info, 
  CheckCircle,
  X,
  ChevronDown,
  ChevronUp,
  Lightbulb,
  BookOpen,
  Wrench
} from 'lucide-react'
import { cn } from '@/lib/utils'

export type AlertSeverity = 'info' | 'warning' | 'critical' | 'success'

export interface Alert {
  id: string
  type: 'info' | 'warning' | 'damage' | 'failure' | 'milestone' | 'recommendation'
  severity: AlertSeverity
  title: string
  message: string
  component?: string
  day?: number
  explanation?: string
  cause?: string
  recommendation?: string
  timestamp: Date
  isRead: boolean
}

interface AlertSystemProps {
  alerts: Alert[]
  onDismiss?: (id: string) => void
  onMarkRead?: (id: string) => void
  maxVisible?: number
}

const severityConfig = {
  info: {
    icon: Info,
    bg: 'bg-primary/10',
    border: 'border-primary/30',
    iconColor: 'text-primary',
    titleColor: 'text-primary',
  },
  warning: {
    icon: AlertTriangle,
    bg: 'bg-warning/10',
    border: 'border-warning/30',
    iconColor: 'text-warning',
    titleColor: 'text-warning',
  },
  critical: {
    icon: XCircle,
    bg: 'bg-danger/10',
    border: 'border-danger/30',
    iconColor: 'text-danger',
    titleColor: 'text-danger',
  },
  success: {
    icon: CheckCircle,
    bg: 'bg-success/10',
    border: 'border-success/30',
    iconColor: 'text-success',
    titleColor: 'text-success',
  },
}

function AlertCard({ alert, onDismiss, onMarkRead }: {
  alert: Alert
  onDismiss?: (id: string) => void
  onMarkRead?: (id: string) => void
}) {
  const [expanded, setExpanded] = useState(false)
  const config = severityConfig[alert.severity]
  const Icon = config.icon

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -20, height: 0 }}
      animate={{ opacity: 1, x: 0, height: 'auto' }}
      exit={{ opacity: 0, x: 20, height: 0 }}
      className={cn(
        'rounded-xl border overflow-hidden',
        config.bg,
        config.border,
        !alert.isRead && 'ring-1 ring-primary/30'
      )}
    >
      <div 
        className="p-4 cursor-pointer"
        onClick={() => {
          setExpanded(!expanded)
          if (!alert.isRead) onMarkRead?.(alert.id)
        }}
      >
        <div className="flex items-start gap-3">
          <div className={cn('p-2 rounded-lg', config.bg)}>
            <Icon className={cn('w-5 h-5', config.iconColor)} />
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <h4 className={cn('font-semibold text-sm', config.titleColor)}>
                {alert.title}
              </h4>
              {alert.day !== undefined && (
                <span className="text-xs text-muted-foreground bg-solar-bg-card px-2 py-0.5 rounded">
                  Day {alert.day}
                </span>
              )}
            </div>
            <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
              {alert.message}
            </p>
            {alert.component && (
              <span className="inline-block mt-2 px-2 py-0.5 bg-solar-bg-card rounded text-xs capitalize">
                {alert.component}
              </span>
            )}
          </div>

          <button
            onClick={(e) => {
              e.stopPropagation()
              onDismiss?.(alert.id)
            }}
            className="p-1 hover:bg-solar-bg-card rounded transition-colors"
          >
            <X className="w-4 h-4 text-muted-foreground" />
          </button>
        </div>

        {/* Expand button */}
        {(alert.explanation || alert.cause || alert.recommendation) && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              setExpanded(!expanded)
            }}
            className="mt-3 flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            {expanded ? 'Hide Details' : 'Show Details'}
          </button>
        )}
      </div>

      {/* Expanded content - Educational overlay */}
      <AnimatePresence>
        {expanded && (alert.explanation || alert.cause || alert.recommendation) && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-solar-border/50 overflow-hidden"
          >
            <div className="p-4 space-y-4 bg-solar-bg/50">
              {/* Explanation */}
              {alert.explanation && (
                <div className="flex gap-3">
                  <div className="p-2 rounded-lg bg-info/10 h-fit">
                    <BookOpen className="w-4 h-4 text-info" />
                  </div>
                  <div>
                    <h5 className="text-xs font-semibold text-info mb-1">What happened?</h5>
                    <p className="text-sm text-muted-foreground">{alert.explanation}</p>
                  </div>
                </div>
              )}

              {/* Cause */}
              {alert.cause && (
                <div className="flex gap-3">
                  <div className="p-2 rounded-lg bg-warning/10 h-fit">
                    <AlertTriangle className="w-4 h-4 text-warning" />
                  </div>
                  <div>
                    <h5 className="text-xs font-semibold text-warning mb-1">Root Cause</h5>
                    <p className="text-sm text-muted-foreground">{alert.cause}</p>
                  </div>
                </div>
              )}

              {/* Recommendation */}
              {alert.recommendation && (
                <div className="flex gap-3">
                  <div className="p-2 rounded-lg bg-success/10 h-fit">
                    <Wrench className="w-4 h-4 text-success" />
                  </div>
                  <div>
                    <h5 className="text-xs font-semibold text-success mb-1">Recommendation</h5>
                    <p className="text-sm text-muted-foreground">{alert.recommendation}</p>
                  </div>
                </div>
              )}

              {/* Key Learning */}
              <div className="flex gap-3 p-3 bg-solar-bg-card rounded-lg">
                <div className="p-2 rounded-lg bg-solar/10 h-fit">
                  <Lightbulb className="w-4 h-4 text-solar" />
                </div>
                <div>
                  <h5 className="text-xs font-semibold text-solar mb-1">Key Learning</h5>
                  <p className="text-sm text-muted-foreground">
                    {alert.type === 'failure' 
                      ? 'System failures often result from accumulated stress over time. Regular monitoring can prevent catastrophic shutdowns.'
                      : alert.type === 'damage'
                      ? 'Deep discharge cycles significantly reduce battery lifespan. Keeping DoD below 50% extends battery life.'
                      : 'Early warnings indicate stress conditions that, if addressed, can prevent system failures.'
                    }
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export function SimulationAlertSystem({
  alerts,
  onDismiss,
  onMarkRead,
  maxVisible = 5,
}: AlertSystemProps) {
  const [showAll, setShowAll] = useState(false)
  const unreadCount = alerts.filter(a => !a.isRead).length

  const visibleAlerts = showAll ? alerts : alerts.slice(0, maxVisible)

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="font-semibold flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-warning" />
            Alerts
          </h3>
          {unreadCount > 0 && (
            <span className="px-2 py-0.5 bg-primary/20 text-primary text-xs font-medium rounded-full">
              {unreadCount} new
            </span>
          )}
        </div>
        <span className="text-sm text-muted-foreground">
          {alerts.length} total
        </span>
      </div>

      {/* Alert list */}
      <div className="space-y-3 max-h-[500px] overflow-y-auto">
        <AnimatePresence mode="popLayout">
          {visibleAlerts.map(alert => (
            <AlertCard
              key={alert.id}
              alert={alert}
              onDismiss={onDismiss}
              onMarkRead={onMarkRead}
            />
          ))}
        </AnimatePresence>
      </div>

      {/* Show more/less */}
      {alerts.length > maxVisible && (
        <button
          onClick={() => setShowAll(!showAll)}
          className="w-full py-2 text-sm text-primary hover:bg-primary/10 rounded-lg transition-colors"
        >
          {showAll ? 'Show less' : `Show ${alerts.length - maxVisible} more alerts`}
        </button>
      )}

      {/* Empty state */}
      {alerts.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          <CheckCircle className="w-12 h-12 mx-auto mb-3 text-success opacity-50" />
          <p className="font-medium">All systems operational</p>
          <p className="text-sm mt-1">No alerts or warnings</p>
        </div>
      )}
    </div>
  )
}

// Toast notification component for real-time alerts
export function AlertToast({ 
  alert, 
  onDismiss 
}: { 
  alert: Alert
  onDismiss: () => void 
}) {
  const config = severityConfig[alert.severity]
  const Icon = config.icon

  return (
    <motion.div
      initial={{ opacity: 0, y: 50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.9 }}
      className={cn(
        'fixed bottom-4 right-4 z-50 w-96 glass-card rounded-xl border-2 overflow-hidden shadow-2xl',
        config.border
      )}
    >
      <div className="p-4">
        <div className="flex items-start gap-3">
          <div className={cn('p-2 rounded-lg animate-pulse', config.bg)}>
            <Icon className={cn('w-5 h-5', config.iconColor)} />
          </div>
          
          <div className="flex-1 min-w-0">
            <h4 className={cn('font-semibold text-sm', config.titleColor)}>
              {alert.title}
            </h4>
            <p className="text-sm text-muted-foreground mt-1">
              {alert.message}
            </p>
          </div>

          <button
            onClick={onDismiss}
            className="p-1 hover:bg-solar-bg-card rounded transition-colors"
          >
            <X className="w-4 h-4 text-muted-foreground" />
          </button>
        </div>
      </div>
    </motion.div>
  )
}
