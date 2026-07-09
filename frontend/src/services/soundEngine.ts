/**
 * Sound Engine Service - Howler.js integration
 * Provides ambient, event, and interaction sounds for the simulation
 */
import { Howl, Howler } from 'howler'

export type SoundType = 
  | 'ambient'
  | 'energyFlow'
  | 'warning'
  | 'critical'
  | 'click'
  | 'success'
  | 'failure'

export interface SoundConfig {
  volume: number
  loop: boolean
  rate?: number
}

// Sound URLs - using free sound effects
const SOUND_URLS: Record<SoundType, string> = {
  ambient: 'https://assets.mixkit.co/active_storage/sfx/212/212-preview.mp3',
  energyFlow: 'https://assets.mixkit.co/active_storage/sfx/2181/2181-preview.mp3',
  warning: 'https://assets.mixkit.co/active_storage/sfx/252/252-preview.mp3',
  critical: 'https://assets.mixkit.co/active_storage/sfx/1195/1195-preview.mp3',
  click: 'https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3',
  success: 'https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3',
  failure: 'https://assets.mixkit.co/active_storage/sfx/267/267-preview.mp3',
}

class SoundEngine {
  private sounds: Map<SoundType, Howl> = new Map()
  private volumes: Map<SoundType, number> = new Map()
  private isInitialized = false
  private masterVolume = 0.5
  private isMuted = false

  /**
   * Initialize all sounds
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) return

    const loadPromises: Promise<void>[] = []

    Object.entries(SOUND_URLS).forEach(([type, url]) => {
      const soundType = type as SoundType
      const isLooping = ['ambient', 'energyFlow'].includes(type)
      
      const sound = new Howl({
        src: [url],
        loop: isLooping,
        volume: this.masterVolume,
        preload: true,
        html5: true, // Better for longer sounds
        onloaderror: (id, error) => {
          console.warn(`Sound ${type} failed to load:`, error)
        },
      })

      this.sounds.set(soundType, sound)
      this.volumes.set(soundType, 0.5)
    })

    // Wait for at least the critical sounds to load
    await Promise.all(loadPromises)
    this.isInitialized = true
    console.log('Sound engine initialized')
  }

  /**
   * Play a sound
   */
  play(type: SoundType, config?: Partial<SoundConfig>): void {
    if (this.isMuted || !this.isInitialized) return

    const sound = this.sounds.get(type)
    if (!sound) return

    const volume = config?.volume ?? this.volumes.get(type) ?? 0.5
    sound.volume(volume * this.masterVolume)

    if (config?.rate) {
      sound.rate(config.rate)
    }

    sound.play()
  }

  /**
   * Stop a sound
   */
  stop(type: SoundType): void {
    const sound = this.sounds.get(type)
    if (sound) {
      sound.stop()
    }
  }

  /**
   * Pause a sound
   */
  pause(type: SoundType): void {
    const sound = this.sounds.get(type)
    if (sound) {
      sound.pause()
    }
  }

  /**
   * Resume a paused sound
   */
  resume(type: SoundType): void {
    const sound = this.sounds.get(type)
    if (sound) {
      sound.play()
    }
  }

  /**
   * Set volume for a specific sound type
   */
  setVolume(type: SoundType, volume: number): void {
    this.volumes.set(type, Math.max(0, Math.min(1, volume)))
    const sound = this.sounds.get(type)
    if (sound) {
      sound.volume(volume * this.masterVolume)
    }
  }

  /**
   * Set master volume
   */
  setMasterVolume(volume: number): void {
    this.masterVolume = Math.max(0, Math.min(1, volume))
    Howler.volume(this.masterVolume)
  }

  /**
   * Mute/unmute all sounds
   */
  setMuted(muted: boolean): void {
    this.isMuted = muted
    if (muted) {
      Howler.mute(true)
    } else {
      Howler.mute(false)
    }
  }

  /**
   * Start ambient loop
   */
  startAmbient(): void {
    this.play('ambient', { volume: 0.15, loop: true })
  }

  /**
   * Update energy flow sound based on load percentage
   */
  updateEnergyFlow(loadPercent: number): void {
    const sound = this.sounds.get('energyFlow')
    if (!sound) return

    // Map load (0-100) to volume (0.1-0.4)
    const volume = 0.1 + (loadPercent / 100) * 0.3
    // Map load to pitch (0.8-1.2)
    const rate = 0.8 + (loadPercent / 100) * 0.4

    if (!sound.playing()) {
      sound.volume(volume * this.masterVolume)
      sound.rate(rate)
      sound.loop(true)
      sound.play()
    } else {
      sound.volume(volume * this.masterVolume)
      sound.rate(rate)
    }
  }

  /**
   * Stop energy flow sound
   */
  stopEnergyFlow(): void {
    this.stop('energyFlow')
  }

  /**
   * Play warning sequence
   */
  playWarning(): void {
    this.play('warning', { volume: 0.4 })
  }

  /**
   * Play critical alert
   */
  playCritical(): void {
    this.play('critical', { volume: 0.6 })
  }

  /**
   * Play UI click
   */
  playClick(): void {
    this.play('click', { volume: 0.3 })
  }

  /**
   * Play success sound
   */
  playSuccess(): void {
    this.play('success', { volume: 0.4 })
  }

  /**
   * Play failure sound
   */
  playFailure(): void {
    this.play('failure', { volume: 0.5 })
  }

  /**
   * Cleanup and stop all sounds
   */
  dispose(): void {
    this.sounds.forEach((sound) => {
      sound.stop()
      sound.unload()
    })
    this.sounds.clear()
    this.isInitialized = false
  }
}

// Singleton instance
export const soundEngine = new SoundEngine()

// React hook for sound engine
import { useEffect, useState, useCallback } from 'react'

export function useSoundEngine() {
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    soundEngine.initialize().then(() => {
      setIsReady(true)
    })

    return () => {
      // Don't dispose on unmount, just pause
    }
  }, [])

  const playSound = useCallback((type: SoundType) => {
    soundEngine.play(type)
  }, [])

  const setMuted = useCallback((muted: boolean) => {
    soundEngine.setMuted(muted)
  }, [])

  return {
    isReady,
    playSound,
    setMuted,
    soundEngine,
  }
}
