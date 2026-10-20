
/** @odoo-module **/

import {
    Component,
    useState,
    useRef,
    onWillStart,
    onMounted,
    onWillUnmount,
} from "@odoo/owl";

import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";

class RecruitmentDashboard extends Component {
    static template = "recruitment_management.RecruitmentDashboard";

    setup() {
        this.action = useService("action");
        this.orm = useService("orm");

        // Chart references
        this.chartRef = useRef("applicationsChart");
        this.departmentChartRef = useRef("departmentChart");

        // Chart instances
        this.chart = null;
        this.departmentChart = null;

        // Dashboard state
        this.state = useState({
            stages: [],
            total_applications: 0,
            open_jobs: 0,
            closed_jobs: 0,
        });

        this.chartData = null;
        this.departmentChartData = null;

        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            await this.loadData();
        });

        onMounted(() => {
            this.renderChart();
            this.renderDepartmentChart();
        });

        onWillUnmount(() => {
            if (this.chart) {
                this.chart.destroy();
                this.chart = null;
            }

            if (this.departmentChart) {
                this.departmentChart.destroy();
                this.departmentChart = null;
            }
        });
    }

    // ---------------------------------------------------------
    // Load dashboard data
    // ---------------------------------------------------------

    async loadData() {
        const stats = await this.orm.call(
            "recruitment.application",
            "get_dashboard_stats",
            [],
        );

        this.state.stages = stats.stages;
        this.state.total_applications = stats.total_applications;
        this.state.open_jobs = stats.open_jobs;
        this.state.closed_jobs = stats.closed_jobs;

        // Applications over time
        this.chartData = await this.orm.call(
            "recruitment.application",
            "get_applications_over_time",
            [],
        );

        // Hires grouped by department
        this.departmentChartData = await this.orm.call(
            "recruitment.application",
            "get_hires_by_department",
            [],
        );
    }

    // ---------------------------------------------------------
    // Applications over time: line chart
    // ---------------------------------------------------------

    renderChart() {
        if (!this.chartRef.el || !this.chartData) {
            return;
        }

        this.chart = new Chart(this.chartRef.el, {
            type: "line",
            data: {
                labels: this.chartData.labels,
                datasets: [
                    {
                        label: "Applications",
                        data: this.chartData.counts,
                        borderColor: "#0d6efd",
                        backgroundColor: "rgba(13, 110, 253, 0.1)",
                        fill: true,
                        tension: 0.3,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0,
                        },
                    },
                },
            },
        });
    }

    // ---------------------------------------------------------
    // Hires by department: bar chart
    // ---------------------------------------------------------

    renderDepartmentChart() {
        if (!this.departmentChartRef.el || !this.departmentChartData) {
            return;
        }

        this.departmentChart = new Chart(this.departmentChartRef.el, {
            type: "bar",
            data: {
                labels: this.departmentChartData.labels,
                datasets: [
                    {
                        label: "Number of Hires",
                        data: this.departmentChartData.counts,
                        backgroundColor: "#198754",
                        borderColor: "#146c43",
                        borderWidth: 1,
                        borderRadius: 5,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0,
                            stepSize: 1,
                        },
                    },
                },
            },
        });
    }

    // ---------------------------------------------------------
    // Open applications by stage
    // ---------------------------------------------------------

    openStage(stage) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: stage.label,
            res_model: "recruitment.application",
            view_mode: "list,kanban,form",
            views: [
                [false, "list"],
                [false, "kanban"],
                [false, "form"],
            ],
            domain: [["state", "=", stage.key]],
            target: "current",
        });
    }

    // ---------------------------------------------------------
    // Open job offers by status
    // ---------------------------------------------------------

    openJobs(jobState) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name:
                jobState === "open"
                    ? "Open Job Offers"
                    : "Closed Job Offers",
            res_model: "recruitment.job",
            view_mode: "kanban,list,form",
            views: [
                [false, "kanban"],
                [false, "list"],
                [false, "form"],
            ],
            domain: [["state", "=", jobState]],
            target: "current",
        });
    }

    // ---------------------------------------------------------
    // Open all applications
    // ---------------------------------------------------------

    openAllApplications() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "All Applications",
            res_model: "recruitment.application",
            view_mode: "list,kanban,form",
            views: [
                [false, "list"],
                [false, "kanban"],
                [false, "form"],
            ],
            target: "current",
        });
    }
}

registry.category("actions").add(
    "recruitment_management.dashboard",
    RecruitmentDashboard,
);
