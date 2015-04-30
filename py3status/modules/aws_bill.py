# -*- coding: utf-8 -*-
"""
Display the current AWS bill.

##### WARNING #####
This module generate some costs on the AWS bill.
Take care about the cache_timeout to limit these fees !
##### WARNING #####

Configuration parameters:
    - aws_access_key_id: Your AWS access key
    - aws_account_id: the root ID of the AWS account.
      Can be found here: https://console.aws.amazon.com/billing/home#/account
    - aws_secret_access_key: Your AWS secret key
    - billing_file: csv file location
    - cache_timeout: how often we refresh this module in seconds
    - s3_bucket_name: the bucket where billing files are sent by AWS.
      Follow this article to activate this feature:
      http://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/detailed-billing-reports.html

Requires:
    - boto

@author nawadanp
"""

import boto
import csv
import datetime

from boto.s3.connection import Key
from time import time


class Py3status:
    """
    """
    # available configuration parameters
    aws_access_key_id = ''
    aws_account_id = ''
    aws_secret_access_key = ''
    billing_file = '/tmp/.aws_billing.csv'
    cache_timeout = 3600
    s3_bucket_name = ''

    def _get_bill_amount(self):
        # Billing file name, generated by Amazon itself
        # Format : 123456789012-aws-billing-csv-yyyy-mm.csv
        s3_file_key = '{}-aws-billing-csv-{}-{}.csv'.format(
            self.aws_account_id, datetime.datetime.now().strftime('%Y'),
            datetime.datetime.now().strftime('%m'))
        i = 0

        # Connection to s3 service
        try:
            conn = boto.connect_s3(self.aws_access_key_id,
                                   self.aws_secret_access_key)
        except:
            return 'conn_error'

        # Connection to the bucket
        try:
            bucket = conn.get_bucket(self.s3_bucket_name)
        except:
            return 'bucket_error'

        # Fetch the objects keys and get the billing file
        try:
            k = Key(bucket)
            k.key = s3_file_key
            k.get_contents_to_filename(self.billing_file)
            k.close
        except:
            return 'key_error'

        # Parse the file and get the InvoiceTotal amount
        try:
            with open(self.billing_file, 'rb') as f:
                reader = csv.reader(f)
                for row in reader:
                    if ''.join(row).find('InvoiceTotal') == -1:
                        continue
                    i = i + 1
                    return row[-1]
        except:
            return 'csv_error'

        return False

    def aws_bill(self, i3s_output_list, i3s_config):
        response = {
            'cached_until': time() + self.cache_timeout,
            'full_text': '',
            'color': i3s_config['color_bad']
        }

        bill_amount = self._get_bill_amount()

        if bill_amount == 'csv_error':
            response['full_text'] = 'Bad CSV file'
        elif bill_amount == 'key_error':
            response['full_text'] = 'Key not found in the bucket'
        elif bill_amount == 'bucket_error':
            response['full_text'] = 'Check the bucket name or your AWS keys'
        elif bill_amount == 'conn_error':
            response['full_text'] = 'Check your internet access'
        elif bill_amount is not False:
            response['full_text'] = str(bill_amount) + '$'
            response['color'] = i3s_config['color_good']
        else:
            response['full_text'] = 'Global error - WTF exception'

        return response


if __name__ == "__main__":
    """
    Test this module by calling it directly.
    """
    from time import sleep
    x = Py3status()
    config = {
        'color_bad': '#FF0000',
        'color_degraded': '#FFFF00',
        'color_good': '#00FF00'
    }
    while True:
        print(x.aws_bill([], config))
        sleep(1)