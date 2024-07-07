import json
import time

from llm_job import create_foreign_keys, convert_comments_to_sql, convert_table_to_sql


def validateReactFlow(data):
    is_invalid = False
    if "description" in data and "nodes" in data:
        for node in data["nodes"]:
            if "data" in node and "columns" in node["data"]:
                for column in node["data"]["columns"]:
                    if "name" not in column or "type" not in column:
                        raise Exception("Missing name or type in column data")
                        is_invalid = True
                        break
            else:
                raise Exception("Missing columns in node data")
                is_invalid = True
                break
    else:
        raise Exception("Missing description or nodes")


    return not is_invalid



class ReactFlowToSQLConverter:
    sleep_time = 60
    def __init__(self, data, technology):
        self.data = data
        self.technology = technology

    def remove_constraints(self, node):
        node["data"]["constraints"] = None
        return node

    def convert(self, callback, only_tables=False, only_comments=False, only_constraints=False):
        finished_tables = 0
        create_table_list = []
        create_comments = []

        total_tables = len(self.data["nodes"])

        if not only_constraints:
            for node in self.data["nodes"]:
                if node["type"] == "table":
                    callback({
                        "type": "table",
                        "name": node["data"]["name"],
                        "columns": node["data"]["columns"],
                        "mode": "start_covnersion"
                    })
                    try:
                        removed_constraints_node = self.remove_constraints(json.loads(json.dumps(node)))

                        data = convert_table_to_sql(removed_constraints_node, self.technology)

                        if data:
                            callback({
                                "result": data.content,
                                "type": "create_table",
                                "table": node["data"]["name"],
                            })

                        time.sleep(self.sleep_time)

                        comments = convert_comments_to_sql(node, self.technology)

                        if comments:
                            callback({
                                "result": comments.content,
                                "type": "create_comments",
                                "table": node["data"]["name"],
                            })

                    except Exception as e:

                        callback({
                            "type": "table",
                            "name": node["data"]["name"],
                            "columns": node["data"]["columns"],
                            "mode": "conversion_error",
                            "error": str(e)
                        })


                    callback({
                        "type": "table",
                        "name": node["data"]["name"],
                        "columns": node["data"]["columns"],
                        "mode": "conversion_done",
                    })

                    finished_tables = finished_tables + 1
                    callback({
                        "progress": finished_tables / total_tables,
                        "mode": "progress"
                    })

                time.sleep(self.sleep_time)


        key_data = create_foreign_keys(self.data["edges"], self.technology)
        callback({
            "result": key_data.content,
            "type": "create_constraints",
            "table": "Constraints",
        })

        callback({
            "mode": "done"
        })

        return create_table_list, create_comments, key_data

