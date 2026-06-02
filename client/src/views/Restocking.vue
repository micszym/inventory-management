<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>

      <!-- Budget Slider Card -->
      <div class="card budget-card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.budget') }}</h3>
          <div class="budget-display">{{ formatCurrency(budget, currentCurrency) }}</div>
        </div>
        <div class="budget-slider-area">
          <input
            v-if="sliderMax > 0"
            type="range"
            class="budget-slider"
            v-model.number="budget"
            :min="0"
            :max="sliderMax"
            :step="sliderStep"
          />
          <div v-else class="budget-slider-empty">
            <input type="range" class="budget-slider" disabled :min="0" :max="1" :value="0" />
          </div>
          <div class="budget-slider-labels">
            <span>{{ formatCurrency(0, currentCurrency) }}</span>
            <span class="budget-help-label">{{ t('restocking.budgetHelp') }}</span>
            <span>{{ formatCurrency(sliderMax, currentCurrency) }}</span>
          </div>
        </div>
      </div>

      <!-- Summary Stats -->
      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.itemsSelected', { count: recommendations.recommendedItems.length }) }}</div>
          <div class="stat-value">{{ recommendations.recommendedItems.length }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('restocking.totalCost') }}</div>
          <div class="stat-value stat-value--currency">{{ formatCurrency(recommendations.totalCost, currentCurrency) }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t('restocking.remainingBudget') }}</div>
          <div class="stat-value stat-value--currency">{{ formatCurrency(recommendations.remainingBudget, currentCurrency) }}</div>
        </div>
      </div>

      <!-- Recommendations Table -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendations') }}</h3>
        </div>

        <div v-if="recommendations.recommendedItems.length === 0" class="no-recommendations">
          {{ t('restocking.noRecommendations') }}
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th class="col-numeric">{{ t('restocking.table.currentDemand') }}</th>
                <th class="col-numeric">{{ t('restocking.table.forecastedDemand') }}</th>
                <th class="col-numeric">{{ t('restocking.table.restockQty') }}</th>
                <th class="col-numeric">{{ t('restocking.table.unitCost') }}</th>
                <th class="col-numeric">{{ t('restocking.table.lineTotal') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recommendations.recommendedItems" :key="item.sku">
                <td><strong>{{ item.sku }}</strong></td>
                <td>{{ item.name }}</td>
                <td>
                  <span :class="['badge', trendBadgeClass(item.trend)]">
                    {{ t(`trends.${item.trend}`) }}
                  </span>
                </td>
                <td class="col-numeric">{{ item.currentDemand.toLocaleString() }}</td>
                <td class="col-numeric">{{ item.forecasted_demand.toLocaleString() }}</td>
                <td class="col-numeric"><strong>{{ item.shortfall.toLocaleString() }}</strong></td>
                <td class="col-numeric">{{ formatCurrency(item.unitCost, currentCurrency) }}</td>
                <td class="col-numeric"><strong>{{ formatCurrency(item.lineCost, currentCurrency) }}</strong></td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="summary-row">
                <td colspan="7" class="summary-label">{{ t('restocking.totalCost') }}</td>
                <td class="col-numeric summary-value">{{ formatCurrency(recommendations.totalCost, currentCurrency) }}</td>
              </tr>
              <tr class="summary-row remaining-row">
                <td colspan="7" class="summary-label">{{ t('restocking.remainingBudget') }}</td>
                <td class="col-numeric summary-value remaining-value">{{ formatCurrency(recommendations.remainingBudget, currentCurrency) }}</td>
              </tr>
            </tfoot>
          </table>
        </div>

        <!-- Place Order Action -->
        <div class="order-action">
          <div v-if="orderSuccess" class="order-success">
            {{ t('restocking.orderPlaced', { orderNumber: placedOrderNumber }) }}
            <button class="btn-link" @click="goToOrders">{{ t('restocking.viewInOrders') }}</button>
          </div>
          <div v-if="orderError" class="error order-error-inline">{{ t('restocking.orderError') }}</div>
          <button
            class="btn-primary"
            :disabled="recommendations.recommendedItems.length === 0 || submitting"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.placing') : t('restocking.placeOrder') }}
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrency } from '../utils/currency'

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency } = useI18n()
    const router = useRouter()

    const loading = ref(true)
    const error = ref(null)
    const allForecasts = ref([])
    const inventoryItems = ref([])

    const budget = ref(0)
    const submitting = ref(false)
    const orderSuccess = ref(false)
    const orderError = ref(false)
    const placedOrderNumber = ref('')

    // ── Data load ───────────────────────────────────────────────────────────
    const loadData = async () => {
      loading.value = true
      error.value = null
      try {
        const [forecastsData, inventoryData] = await Promise.all([
          api.getDemandForecasts(),
          api.getInventory()   // no filters — unit_cost must always be present
        ])
        allForecasts.value = forecastsData
        inventoryItems.value = inventoryData
      } catch (err) {
        error.value = 'Failed to load restocking data: ' + err.message
        console.error(err)
      } finally {
        loading.value = false
      }
    }

    // ── Candidates (computed) ───────────────────────────────────────────────
    // Forecast-driven: shortfall = forecasted_demand - current_demand (growth).
    // Keeps only items with positive growth; sorts by growth descending so the
    // fastest-growing items are prioritised first by the greedy recommender.
    const candidates = computed(() => {
      const inventoryBySku = {}
      for (const inv of inventoryItems.value) {
        inventoryBySku[inv.sku] = inv
      }

      // Fallback unit cost: average across all loaded inventory items.
      // Used when a forecast SKU has no matching inventory row (e.g. demand
      // forecasts cover future/planned SKUs not yet stocked in the warehouse).
      const avgUnitCost = (() => {
        const items = inventoryItems.value
        if (!items.length) return 0
        const total = items.reduce((sum, inv) => sum + (inv.unit_cost || 0), 0)
        return total / items.length
      })()

      const result = []
      for (const forecast of allForecasts.value) {
        const growth = forecast.forecasted_demand - forecast.current_demand
        if (growth <= 0) continue

        const inv = inventoryBySku[forecast.item_sku]
        const unitCost = inv ? inv.unit_cost : avgUnitCost

        result.push({
          sku: forecast.item_sku,
          name: forecast.item_name,
          trend: forecast.trend,
          currentDemand: forecast.current_demand,
          forecasted_demand: forecast.forecasted_demand,
          shortfall: growth,
          unitCost,
          lineCost: growth * unitCost
        })
      }

      return result.sort((a, b) => b.shortfall - a.shortfall)
    })

    // ── Slider bounds ───────────────────────────────────────────────────────
    const sliderMax = computed(() => {
      const total = candidates.value.reduce((sum, c) => sum + c.lineCost, 0)
      return Math.ceil(total)
    })

    const sliderStep = computed(() => {
      if (sliderMax.value <= 0) return 1000
      return Math.max(1000, Math.round(sliderMax.value / 100))
    })

    // Default budget to ~50% of max whenever candidates change (e.g. after load)
    watch(sliderMax, (newMax) => {
      if (newMax > 0) {
        const half = newMax / 2
        const step = Math.max(1000, Math.round(newMax / 100))
        budget.value = Math.round(half / step) * step
      } else {
        budget.value = 0
      }
    }, { immediate: false })

    // ── Recommendations (computed) ──────────────────────────────────────────
    // Greedy skip-and-continue: iterate candidates in priority order (highest
    // shortfall first). Include a candidate when its lineCost fits within the
    // remaining budget; if it doesn't fit, skip it and continue checking lower-
    // priority candidates — cheaper items later in the list may still fit.
    // This produces the maximum number of covered items for the given budget.
    const recommendations = computed(() => {
      let remaining = budget.value
      const recommendedItems = []

      for (const candidate of candidates.value) {
        if (candidate.lineCost <= remaining) {
          recommendedItems.push(candidate)
          remaining -= candidate.lineCost
        }
        // do not break — keep checking cheaper items further down the list
      }

      const totalCost = budget.value - remaining
      return {
        recommendedItems,
        totalCost,
        remainingBudget: remaining
      }
    })

    // ── Helpers ─────────────────────────────────────────────────────────────
    const trendBadgeClass = (trend) => {
      // Mirror the badge classes already defined in App.vue global styles
      const map = {
        increasing: 'increasing',
        stable: 'stable',
        decreasing: 'decreasing'
      }
      return map[trend] || 'info'
    }

    // ── Place Order ─────────────────────────────────────────────────────────
    const placeOrder = async () => {
      if (recommendations.value.recommendedItems.length === 0 || submitting.value) return

      submitting.value = true
      orderSuccess.value = false
      orderError.value = false

      const items = recommendations.value.recommendedItems.map(i => ({
        sku: i.sku,
        name: i.name,
        quantity: i.shortfall,
        unit_price: i.unitCost
      }))

      try {
        const result = await api.createOrder({ items })
        placedOrderNumber.value = result.order_number || result.id || ''
        orderSuccess.value = true
      } catch (err) {
        orderError.value = true
        console.error('Failed to place restock order:', err)
      } finally {
        submitting.value = false
      }
    }

    const goToOrders = () => {
      router.push('/orders')
    }

    onMounted(loadData)

    return {
      t,
      currentCurrency,
      formatCurrency,
      loading,
      error,
      budget,
      sliderMax,
      sliderStep,
      candidates,
      recommendations,
      submitting,
      orderSuccess,
      orderError,
      placedOrderNumber,
      trendBadgeClass,
      placeOrder,
      goToOrders
    }
  }
}
</script>

<style scoped>
/* ── Budget card ─────────────────────────────────────────────────── */
.budget-card .card-header {
  align-items: flex-start;
}

.budget-display {
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
  white-space: nowrap;
}

.budget-slider-area {
  padding-top: 0.5rem;
}

.budget-slider {
  width: 100%;
  appearance: none;
  -webkit-appearance: none;
  height: 6px;
  border-radius: 4px;
  background: #e2e8f0;
  outline: none;
  cursor: pointer;
  accent-color: #2563eb;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 4px rgba(37, 99, 235, 0.4);
  transition: box-shadow 0.15s ease;
}

.budget-slider::-webkit-slider-thumb:hover {
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.15);
}

.budget-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 4px rgba(37, 99, 235, 0.4);
}

.budget-slider:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.budget-slider-labels {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.625rem;
  font-size: 0.813rem;
  color: #64748b;
}

.budget-help-label {
  color: #94a3b8;
  font-style: italic;
}

/* ── Stat value override for currency strings ─────────────────────── */
.stat-value--currency {
  font-size: 1.5rem;
}

/* ── Table numeric columns ───────────────────────────────────────── */
.col-numeric {
  text-align: right;
}

/* ── Table footer summary rows ───────────────────────────────────── */
tfoot .summary-row td {
  border-top: 2px solid #e2e8f0;
  padding: 0.625rem 0.75rem;
  font-size: 0.875rem;
  background: #f8fafc;
}

.summary-label {
  font-weight: 600;
  color: #475569;
  text-align: right;
}

.summary-value {
  font-weight: 700;
  color: #0f172a;
}

.remaining-row .summary-value.remaining-value {
  color: #059669;
}

/* ── Empty state ─────────────────────────────────────────────────── */
.no-recommendations {
  padding: 2.5rem 1rem;
  text-align: center;
  color: #64748b;
  font-size: 0.938rem;
}

/* ── Order action area ───────────────────────────────────────────── */
.order-action {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding-top: 1.25rem;
  border-top: 1px solid #e2e8f0;
  margin-top: 0.5rem;
  flex-wrap: wrap;
}

.btn-primary {
  background: #2563eb;
  color: #ffffff;
  border: none;
  padding: 0.625rem 1.5rem;
  border-radius: 6px;
  font-size: 0.938rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease, opacity 0.15s ease;
  white-space: nowrap;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-primary:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.order-success {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #d1fae5;
  color: #065f46;
  padding: 0.625rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  flex: 1;
  min-width: 0;
}

.btn-link {
  background: none;
  border: none;
  color: #2563eb;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
  white-space: nowrap;
}

.btn-link:hover {
  color: #1d4ed8;
}

.order-error-inline {
  margin: 0;
  flex: 1;
  min-width: 0;
}
</style>
