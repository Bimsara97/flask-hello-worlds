// Main JavaScript for Soil Health Monitoring App

document.addEventListener('DOMContentLoaded', function() {
    console.log('Document loaded, initializing app...');

    // Handle file upload
    const imageUpload = document.getElementById('imageUpload');
    const uploadPreview = document.getElementById('uploadPreview');
    const fileName = document.getElementById('fileName');
    const clearImageBtn = document.getElementById('clearImageBtn');

    if (imageUpload) {
        console.log('Found image upload element');

        imageUpload.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                console.log('File selected:', this.files[0].name);

                // Update UI with selected filename
                fileName.textContent = this.files[0].name;
                uploadPreview.classList.remove('d-none');

                // Optional: Preview image
                // const reader = new FileReader();
                // reader.onload = function(e) {
                //     // Preview code here if desired
                // }
                // reader.readAsDataURL(this.files[0]);
            }
        });

        // Handle clearing the file selection
        if (clearImageBtn) {
            clearImageBtn.addEventListener('click', function() {
                imageUpload.value = '';
                uploadPreview.classList.add('d-none');
                console.log('File selection cleared');
            });
        }
    }

    // Form submission - Standard form submission
    const analysisForm = document.getElementById('analysisForm');

    if (analysisForm) {
        console.log('Found analysis form');

        analysisForm.addEventListener('submit', function(e) {
            console.log('Form submitted');

            // Show loading indicators
            const resultsSection = document.getElementById('resultsSection');
            const loadingIndicator = document.getElementById('loadingIndicator');
            const resultsContent = document.getElementById('resultsContent');

            if (resultsSection && loadingIndicator && resultsContent) {
                resultsSection.classList.remove('d-none');
                loadingIndicator.classList.remove('d-none');
                resultsContent.innerHTML = '';
                console.log('Loading indicators displayed');
            }

            // Log form data for debugging
            const formData = new FormData(this);
            console.log('Form data entries:');
            for (const [key, value] of formData.entries()) {
                if (key === 'image') {
                    console.log('Image file:', value.name, 'Size:', value.size);
                } else {
                    console.log(key, ':', value);
                }
            }

            // Let the form submit normally
            return true;
        });
    }

    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});

// Function to format numbers with commas
function formatNumber(number) {
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Function to calculate percentage
function calculatePercentage(value, total) {
    return ((value / total) * 100).toFixed(1);
}

// Function to determine status color
function getStatusColor(status) {
    switch(status) {
        case 'deficient':
            return '#dc3545';  // danger
        case 'low':
            return '#ffc107';  // warning
        case 'optimal':
            return '#28a745';  // success
        case 'excessive':
            return '#6c757d';  // secondary
        default:
            return '#17a2b8';  // info
    }
}

// Function to determine status color for temperature
function getTemperatureColor(status) {
    switch(status) {
        case 'cold':
            return '#17a2b8';  // info
        case 'cool':
            return '#007bff';  // primary
        case 'optimal':
            return '#28a745';  // success
        case 'hot':
            return '#ffc107';  // warning
        case 'extreme':
            return '#dc3545';  // danger
        default:
            return '#6c757d';  // secondary
    }
}

// Function to determine disease severity color
function getDiseaseColor(severity) {
    switch(severity) {
        case 'high':
            return '#dc3545';  // danger
        case 'medium':
            return '#ffc107';  // warning
        case 'low':
            return '#17a2b8';  // info
        case 'none':
            return '#28a745';  // success
        default:
            return '#6c757d';  // secondary
    }
}

// Function to initialize all charts
function initializeCharts(data) {
    console.log('Initializing charts with data:', data);

    // Initialize Nutrient Chart
    const nutrientCtx = document.getElementById('nutrientChart');
    if (nutrientCtx) {
        console.log('Creating nutrient chart');
        // Set up the ranges
        const optimalRanges = [];
        for (let i = 0; i < data.nutrientNames.length; i++) {
            optimalRanges.push({
                low: data.nutrientRangesLow[i],
                high: data.nutrientRangesHigh[i]
            });
        }

        // Create the chart
        new Chart(nutrientCtx, {
            type: 'bar',
            data: {
                labels: data.nutrientNames,
                datasets: [
                    {
                        label: 'Nutrient Levels',
                        data: data.nutrientValues,
                        backgroundColor: data.nutrientNames.map((name, i) => {
                            const val = data.nutrientValues[i];
                            const range = optimalRanges[i];

                            if (val < range.low) {
                                return 'rgba(220, 53, 69, 0.7)'; // Deficient - red
                            } else if (val <= range.high) {
                                return 'rgba(40, 167, 69, 0.7)'; // Optimal - green
                            } else {
                                return 'rgba(108, 117, 125, 0.7)'; // Excessive - gray
                            }
                        }),
                        borderColor: 'rgba(0, 0, 0, 0.1)',
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
                                return `${value.toFixed(2)} ${unit}`;
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

    // Initialize Irrigation Chart
    const irrigationCtx = document.getElementById('irrigationChart');
    if (irrigationCtx) {
        console.log('Creating irrigation chart');
        // Create the chart
        new Chart(irrigationCtx, {
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

    // Initialize Disease Chart
    const diseaseCtx = document.getElementById('diseaseChart');
    if (diseaseCtx) {
        console.log('Creating disease chart');

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
        new Chart(diseaseCtx, {
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
}