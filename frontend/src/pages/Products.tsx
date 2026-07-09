import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Search, 
  Filter, 
  CheckCircle, 
  Battery, 
  Zap, 
  Sun,
  ChevronDown,
  Grid3X3,
  List
} from 'lucide-react'
import { cn } from '@/lib/utils'
import type { Product } from '@/types'

// Mock data for demonstration
const mockProducts: Product[] = [
  { id: 1, model_name: 'PG-001', product_name: 'Powerwall 2', company: 'Tesla', category: 'battery', is_verified: true, validation_status: 'approved' },
  { id: 2, model_name: 'SE5000H', product_name: 'SolarEdge SE5000H', company: 'SolarEdge', category: 'inverter', is_verified: true, validation_status: 'approved' },
  { id: 3, model_name: 'LG400N2W', product_name: 'NeON 2 400W', company: 'LG', category: 'panel', is_verified: true, validation_status: 'approved' },
  { id: 4, model_name: 'MPPT-100/30', product_name: 'SmartSolar MPPT', company: 'Victron', category: 'charge_controller', is_verified: true, validation_status: 'approved' },
  { id: 5, model_name: 'HP-10000', product_name: 'PowerMax 10kWh', company: 'BYD', category: 'battery', is_verified: true, validation_status: 'approved' },
  { id: 6, model_name: 'SMA5000', product_name: 'Sunny Boy 5.0', company: 'SMA', category: 'inverter', is_verified: true, validation_status: 'approved' },
  { id: 7, model_name: 'CS3W-400', product_name: 'Hi-MO 4 400W', company: 'LONGi', category: 'panel', is_verified: true, validation_status: 'approved' },
  { id: 8, model_name: 'Tracer-40A', product_name: 'Tracer MPPT 40A', company: 'Epever', category: 'charge_controller', is_verified: false, validation_status: 'pending' },
]

const categories = [
  { id: 'all', name: 'All Products', icon: Grid3X3 },
  { id: 'battery', name: 'Batteries', icon: Battery },
  { id: 'inverter', name: 'Inverters', icon: Zap },
  { id: 'panel', name: 'Solar Panels', icon: Sun },
  { id: 'charge_controller', name: 'Charge Controllers', icon: Zap },
]

export function Products() {
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)

  const filteredProducts = mockProducts.filter((product) => {
    const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory
    const matchesSearch = 
      product.product_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      product.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
      product.model_name.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesCategory && matchesSearch
  })

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl font-bold"
        >
          Product <span className="gradient-text">Catalog</span>
        </motion.h1>
        <p className="text-muted-foreground mt-1">
          Browse and select verified solar components
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col lg:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search products..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-solar-bg-card border border-solar-border rounded-xl focus:outline-none focus:border-primary transition-colors"
          />
        </div>

        {/* View Toggle */}
        <div className="flex items-center gap-2 bg-solar-bg-card rounded-xl p-1">
          <button
            onClick={() => setViewMode('grid')}
            className={cn(
              'p-2 rounded-lg transition-colors',
              viewMode === 'grid' ? 'bg-primary text-white' : 'hover:bg-solar-bg'
            )}
          >
            <Grid3X3 className="w-5 h-5" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={cn(
              'p-2 rounded-lg transition-colors',
              viewMode === 'list' ? 'bg-primary text-white' : 'hover:bg-solar-bg'
            )}
          >
            <List className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Category Sidebar */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-1 space-y-2"
        >
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={cn(
                'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-left',
                selectedCategory === category.id
                  ? 'bg-primary/10 text-primary border border-primary/20'
                  : 'hover:bg-solar-bg-card text-muted-foreground hover:text-foreground'
              )}
            >
              <category.icon className="w-5 h-5" />
              <span className="font-medium">{category.name}</span>
            </button>
          ))}
        </motion.div>

        {/* Products Grid */}
        <div className={cn(
          'lg:col-span-3',
          viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4' : 'space-y-4'
        )}>
          {filteredProducts.map((product, index) => (
            <motion.div
              key={product.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => setSelectedProduct(product)}
              className={cn(
                'glass-card rounded-2xl p-6 cursor-pointer hover:border-primary/30 transition-all',
                viewMode === 'list' && 'flex items-center gap-6'
              )}
            >
              {/* Category Icon */}
              <div className={cn(
                'w-14 h-14 rounded-xl flex items-center justify-center mb-4',
                viewMode === 'list' && 'mb-0 flex-shrink-0',
                product.category === 'battery' && 'bg-success/20 text-success',
                product.category === 'inverter' && 'bg-primary/20 text-primary',
                product.category === 'panel' && 'bg-solar/20 text-solar',
                product.category === 'charge_controller' && 'bg-info/20 text-info'
              )}>
                {product.category === 'battery' && <Battery className="w-7 h-7" />}
                {product.category === 'inverter' && <Zap className="w-7 h-7" />}
                {product.category === 'panel' && <Sun className="w-7 h-7" />}
                {product.category === 'charge_controller' && <Zap className="w-7 h-7" />}
              </div>

              <div className="flex-1">
                {/* Header */}
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="font-semibold text-lg">{product.product_name}</h3>
                    <p className="text-sm text-muted-foreground">{product.company}</p>
                  </div>
                  {product.is_verified && (
                    <div className="flex items-center gap-1 px-2 py-1 bg-success/10 text-success rounded-full text-xs">
                      <CheckCircle className="w-3 h-3" />
                      Verified
                    </div>
                  )}
                </div>

                {/* Model */}
                <p className="text-sm text-muted-foreground mb-4">
                  Model: {product.model_name}
                </p>

                {/* Specs Preview */}
                <div className="flex flex-wrap gap-2">
                  {product.category === 'battery' && (
                    <>
                      <span className="px-2 py-1 bg-solar-bg rounded-lg text-xs">48V</span>
                      <span className="px-2 py-1 bg-solar-bg rounded-lg text-xs">200Ah</span>
                      <span className="px-2 py-1 bg-solar-bg rounded-lg text-xs">4000 cycles</span>
                    </>
                  )}
                  {product.category === 'inverter' && (
                    <>
                      <span className="px-2 py-1 bg-solar-bg rounded-lg text-xs">5000W</span>
                      <span className="px-2 py-1 bg-solar-bg rounded-lg text-xs">99.2% eff</span>
                      <span className="px-2 py-1 bg-solar-bg rounded-lg text-xs">MPPT</span>
                    </>
                  )}
                  {product.category === 'panel' && (
                    <>
                      <span className="px-2 py-1 bg-solar-bg rounded-lg text-xs">400W</span>
                      <span className="px-2 py-1 bg-solar-bg rounded-lg text-xs">22.5% eff</span>
                      <span className="px-2 py-1 bg-solar-bg rounded-lg text-xs">25yr warranty</span>
                    </>
                  )}
                  {product.category === 'charge_controller' && (
                    <>
                      <span className="px-2 py-1 bg-solar-bg rounded-lg text-xs">30A</span>
                      <span className="px-2 py-1 bg-solar-bg rounded-lg text-xs">100V max</span>
                      <span className="px-2 py-1 bg-solar-bg rounded-lg text-xs">MPPT</span>
                    </>
                  )}
                </div>
              </div>

              {/* Arrow */}
              <ChevronDown className={cn(
                'w-5 h-5 text-muted-foreground transition-transform',
                viewMode === 'list' && 'rotate-[-90deg]'
              )} />
            </motion.div>
          ))}
        </div>
      </div>

      {/* Empty State */}
      {filteredProducts.length === 0 && (
        <div className="text-center py-16">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-solar-bg-card flex items-center justify-center">
            <Search className="w-8 h-8 text-muted-foreground" />
          </div>
          <p className="text-lg font-medium">No products found</p>
          <p className="text-muted-foreground mt-1">Try adjusting your search or filters</p>
        </div>
      )}
    </div>
  )
}
