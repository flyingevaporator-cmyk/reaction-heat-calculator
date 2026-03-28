import type { ProcessData, MaterialBalanceResult, HeatBalanceResult } from './types'

const BALANCE_TOLERANCE = 0.01 // 1% tolerance

export function calcMaterialBalance(data: ProcessData): MaterialBalanceResult[] {
  const results: MaterialBalanceResult[] = []

  for (const step of data.steps) {
    const inputStreams = data.streams.filter(s => step.inputStreams.includes(s.id))
    const outputStreams = data.streams.filter(s => step.outputStreams.includes(s.id))

    // Collect all component names
    const allComponents = new Set<string>()
    for (const s of [...inputStreams, ...outputStreams]) {
      for (const c of s.components) {
        allComponents.add(c.name)
      }
    }

    const componentDetails: MaterialBalanceResult['componentDetails'] = []
    let inputTotal = 0
    let outputTotal = 0

    for (const comp of allComponents) {
      const inFlow = inputStreams.reduce((sum, s) => {
        const c = s.components.find(x => x.name === comp)
        return sum + (c ? c.flowRate : 0)
      }, 0)
      const outFlow = outputStreams.reduce((sum, s) => {
        const c = s.components.find(x => x.name === comp)
        return sum + (c ? c.flowRate : 0)
      }, 0)
      inputTotal += inFlow
      outputTotal += outFlow
      componentDetails.push({
        component: comp,
        input: inFlow,
        output: outFlow,
        diff: inFlow - outFlow,
      })
    }

    // Also sum components not named
    if (allComponents.size === 0) {
      inputTotal = inputStreams.reduce((sum, s) =>
        sum + s.components.reduce((ss, c) => ss + c.flowRate, 0), 0)
      outputTotal = outputStreams.reduce((sum, s) =>
        sum + s.components.reduce((ss, c) => ss + c.flowRate, 0), 0)
    }

    const difference = inputTotal - outputTotal
    const balanced = inputTotal === 0 && outputTotal === 0
      ? true
      : Math.abs(difference) / Math.max(inputTotal, outputTotal, 1) <= BALANCE_TOLERANCE

    results.push({
      stepId: step.id,
      stepName: step.name,
      inputTotal,
      outputTotal,
      difference,
      balanced,
      componentDetails,
    })
  }

  return results
}

export function calcHeatBalance(data: ProcessData): HeatBalanceResult[] {
  const results: HeatBalanceResult[] = []

  for (const step of data.steps) {
    const inputStreams = data.streams.filter(s => step.inputStreams.includes(s.id))
    const outputStreams = data.streams.filter(s => step.outputStreams.includes(s.id))

    // Q = m * Cp * T  (reference: 0°C)
    const inputHeat = inputStreams.reduce((sum, s) => {
      const totalMass = s.components.reduce((m, c) => m + c.flowRate, 0)
      return sum + totalMass * s.specificHeat * s.temperature
    }, 0)

    const outputHeat = outputStreams.reduce((sum, s) => {
      const totalMass = s.components.reduce((m, c) => m + c.flowRate, 0)
      return sum + totalMass * s.specificHeat * s.temperature
    }, 0)

    // Reaction heat from output streams (convention: positive = exothermic)
    const reactionHeat = outputStreams.reduce((sum, s) => sum + s.reactionHeat, 0)

    // Required heat = output - input - reaction heat
    // Positive means heating needed, negative means cooling needed
    const requiredHeat = outputHeat - inputHeat - reactionHeat

    results.push({
      stepId: step.id,
      stepName: step.name,
      inputHeat,
      outputHeat,
      reactionHeat,
      requiredHeat,
    })
  }

  return results
}
