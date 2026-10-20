/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

class RecruitmentDashboard extends Component {
    static template = "recruitment_management.RecruitmentDashboard";

    setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        this.state = useState({
            stages: [],
            total_applications: 0,
            open_jobs: 0,
            closed_jobs: 0,
        });
        onWillStart(async () => await this.loadData());
    }

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
    }

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

    openJobs(jobState) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: jobState === "open" ? "Open Job Offers" : "Closed Job Offers",
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