document.addEventListener('DOMContentLoaded', function () {
    const radarCanvas = document.getElementById('radarChart');
    if (!radarCanvas) return;

    // 从全局变量中获取 radar_scores 数据
    const radarScores = window.radarScores;

    const ctx = radarCanvas.getContext('2d');
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Collaboration', 'Communication', 'Participation', 'Respect', 'Consistency'],
            datasets: [{
                label: 'Team Radar Profile',
                data: [
                    radarScores.collaboration,
                    radarScores.communication,
                    radarScores.participation,
                    radarScores.respect,
                    radarScores.consistency
                ],
                fill: true,
                backgroundColor: "rgba(54, 162, 235, 0.2)",
                borderColor: "rgba(54, 162, 235, 1)",
                pointBackgroundColor: "rgba(54, 162, 235, 1)"
            }]
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: {
                        stepSize: 20
                    },
                    pointLabels: {
                        font: {
                            size: 14
                        }
                    }
                }
            }
        }
    });
});
