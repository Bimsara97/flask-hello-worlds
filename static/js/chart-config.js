// Chart Configuration for Soil Health Monitoring App

function initializeCharts(data) {
    // Initialize Nutrient Chart
    initializeNutrientChart(data);
    
    // Initialize Irrigation Chart
    initializeIrrigationChart(data);
    
    // Initialize Disease Chart
    initializeDiseaseChart(data);
}

function initializeNutrientChart(data) {
    const ctx = document.getElementById('nutrientChart');
    if (!ctx) return;
    
    // Set up the ranges
    const optimalRanges = [];
    for (let i = 0; i < data.nutrientNames.length; i++) {
        optimalRanges.push({
            low: data.nutrientRangesLow[i],
            high: data.nutrientRangesHigh[i]
        });
    }
    
    // Create the chart
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.nutrientNames,
            datasets: [
                {
                    label: 'Nutrient Levels',
                    data: data.nutrientValues,
                    backgroundColor: getBarColors(data.nutrientValues, optimalRanges),
                    borderColor: getBarColors(data.nutrientValues, optimalRanges),
                    borderWidth: 1
                },
                {
                    label: 'Optimal Low',
                    data: data.nutrientRangesLow,
                    type: 'line',
                    fill: false,
                    borderColor: 'rgba(255, 193, 7, 0.7)',
                    borderDash: [5, 5],
                    pointRadius: 0,
                    borderWidth: 2
                },
                {
                    label: 'Optimal High',
                    data: data.nutrientRangesHigh,
                    type: 'line',
                    fill: false,
                    borderColor: 'rgba(220, 53, 69, 0.7)',
                    borderDash: [5, 5],
                    pointRadius: 0,
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const index = context.dataIndex;
                            const value = context.raw;
                            const unit = data.nutrientUnits[index];
                            return `${value} ${unit}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        display: true,
                        drawBorder: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function initializeIrrigationChart(data) {
    const ctx = document.getElementById('irrigationChart');
    if (!ctx) return;
    
    // Create the chart
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.irrigationLabels,
            datasets: [{
                label: 'Water (mm)',
                data: data.irrigationValues,
                backgroundColor: [
                    'rgba(23, 162, 184, 0.7)',  // Total Need
                    'rgba(0, 123, 255, 0.7)',    // Rainfall
                    'rgba(40, 167, 69, 0.7)'     // Irrigation Required
                ],
                borderColor: [
                    'rgba(23, 162, 184, 1)',
                    'rgba(0, 123, 255, 1)',
                    'rgba(40, 167, 69, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            return `${value.toFixed(1)} mm`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        display: true,
                        drawBorder: false
                    },
                    title: {
                        display: true,
                        text: 'Amount (mm)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function initializeDiseaseChart(data) {
    const ctx = document.getElementById('diseaseChart');
    if (!ctx) return;
    
    // Sort data by probability for better visualization
    let sortedIndices = [];
    for (let i = 0; i < data.diseaseLabels.length; i++) {
        sortedIndices.push(i);
    }
    
    sortedIndices.sort((a, b) => data.diseaseProbabilities[b] - data.diseaseProbabilities[a]);
    
    let sortedLabels = sortedIndices.map(i => data.diseaseLabels[i]);
    let sortedValues = sortedIndices.map(i => data.diseaseProbabilities[i]);
    
    // Only show top 5 diseases for clarity
    if (sortedLabels.length > 5) {
        sortedLabels = sortedLabels.slice(0, 5);
        sortedValues = sortedValues.slice(0, 5);
    }
    
    // Generate colors with higher opacity for higher probabilities
    const barColors = sortedValues.map(value => {
        const opacity = 0.4 + (value * 0.6); // Scale opacity based on probability
        return `rgba(40, 167, 69, ${opacity})`;
    });
    
    // Create the chart
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedLabels,
            datasets: [{
                label: 'Probability',
                data: sortedValues,
                backgroundColor: barColors,
                borderColor: barColors.map(color => color.replace('rgba', 'rgb').replace(/,\s*[\d.]+\)/, ')')),
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            return `Probability: ${(value * 100).toFixed(1)}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 1,
                    grid: {
                        display: true,
                        drawBorder: false
                    },
                    ticks: {
                        callback: function(value) {
                            return (value * 100) + '%';
                        }
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Helper function to get bar colors based on value ranges
function getBarColors(values, ranges) {
    return values.map((value, index) => {
        const range = ranges[index];
        
        if (value < range.low) {
            return 'rgba(220, 53, 69, 0.7)'; // Deficient - red
        } else if (value <= range.high) {
            return 'rgba(40, 167, 69, 0.7)'; // Optimal - green
        } else {
            return 'rgba(108, 117, 125, 0.7)'; // Excessive - gray
        }
    });
}